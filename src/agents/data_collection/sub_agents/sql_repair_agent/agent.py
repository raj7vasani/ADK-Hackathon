"""
SQL Repair Agent
───────────────────────────────────────────────────────────────────────────────
This agent is part of the Data Collection SequentialAgent pipeline.

🧠 Purpose:
If the SQL Validator Agent returns an "invalid: ..." status, this agent:
1. Regenerates the SQL query using the original user request, the invalid SQL, and the validator error.
2. Stores the regenerated SQL back into session.state["sql_query"].
3. Immediately re-validates the new SQL using the same validator agent.
4. Updates session.state["validation_status"] accordingly.

If the original query was already valid, this agent does nothing.

Inputs expected in session.state:
- "sql_query":      The SQL query string generated earlier.
- "user_request":   The user's original request prompt.
- "validation_status": Result of the first SQLValidatorLLM step (must start with "invalid" to trigger repair).

Outputs written to session.state:
- "sql_query":      Updated regenerated SQL if repaired.
- "validation_status": Validation result of the retried query.

The agent emits a short confirmation event when a retry is performed.
"""

from __future__ import annotations

from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types


class SqlRepairAgent(BaseAgent):
    name = "SqlRepairAgent"
    description = "Regenerates SQL if the validator reports a failure."

    def __init__(self):
        # Deferred imports to avoid circular issues in agent trees
        from src.agents.data_collection.sub_agents.sql_generator.agent import sql_generator_agent
        from src.agents.data_collection.sub_agents.sql_validator.agent import sql_validator_llm

        self.generator = sql_generator_agent
        self.validator = sql_validator_llm

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state

        validation_status = state.get("validation_status", "")
        if validation_status.startswith("valid"):
            return  # No repair needed

        bad_sql = state.get("sql_query", "")
        user_request = state.get("user_request", "")

        if not bad_sql or not user_request:
            yield Event.from_content(ctx, "⚠️ Missing SQL or user request in state.")
            return

        # ─────────────────────────────────────────────────────────────────────
        # Generate corrected SQL using the validation error and original input
        # ─────────────────────────────────────────────────────────────────────
        retry_prompt = f"""
            The following SQL query was invalid:

            ```sql
            {bad_sql}
            Validation error:
            {validation_status}

            Please regenerate a correct BigQuery SQL query that fulfills the original user request:

            "{user_request}"

            Make sure the new SQL:

            Corrects the above error
            Is syntactically correct
            Is compatible with BigQuery
            Uses valid clauses and schema references
            Return ONLY the corrected SQL without extra commentary.
            """
        
        new_sql = self.generator.run(prompt=retry_prompt).get("sql_query", "").strip()
        if not new_sql:
            yield Event.from_content(ctx, "⚠️ SQL regeneration failed: empty result.")
            return

        # Update state with new query and re-validate
        state["sql_query"] = new_sql
        state["validation_status"] = self.validator.run(sql_query=new_sql).get("validation_status", "").strip()

        yield Event.from_content(ctx, "🔄 SQL regenerated and revalidated.")