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
from typing import Any, AsyncGenerator
from pydantic import PrivateAttr        # ← import this
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
import asyncio


class SqlRepairAgent(BaseAgent):
    # ──────────────────────────────────────────────────────────────────────
    # Declare private attributes that Pydantic should ignore at runtime
    # ──────────────────────────────────────────────────────────────────────
    _generator: Any = PrivateAttr()
    _validator: Any = PrivateAttr()

    def __init__(self) -> None:
        super().__init__(
            name="SqlRepairAgent",
            description="Regenerates SQL if the validator reports a failure.",
        )

        # Lazy import to dodge circular-import headaches
        from data_collection.sub_agents.sql_generator.agent import (
            sql_generation_agent,
        )
        from data_collection.sub_agents.sql_validator.agent import sql_validator_llm

        # Save the other agents on the private attrs
        self._generator = sql_generation_agent
        self._validator = sql_validator_llm

    # ------------------------------------------------------------------
    # Implementation
    # ------------------------------------------------------------------
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.state
        validation_status: str = state.get("validation_status", "")

        if validation_status.startswith("valid"):
            return  # Already good; nothing to do

        bad_sql = state.get("sql_query", "")
        user_request = state.get("user_request", "")

        if not bad_sql or not user_request:
            yield Event.from_content(
                ctx, "⚠️ Missing sql_query or user_request in state."
            )
            return

        retry_prompt = f"""
            The following SQL query was invalid:

            ```sql
            {bad_sql}
            Validator said:
            {validation_status}

            Please regenerate a correct BigQuery SQL statement that fulfils:
            "{user_request}"
            Return only the SQL, no commentary.
            """

        new_sql = (
            self._generator.run(prompt=retry_prompt).get("sql_query", "").strip()
        )
        if not new_sql:
            yield Event.from_content(ctx, "⚠️ SQL regeneration returned empty text.")
            return

        state["sql_query"] = new_sql
        state["validation_status"] = (
            self._validator.run(sql_query=new_sql).get("validation_status", "").strip()
        )
sql_repair_agent = SqlRepairAgent()