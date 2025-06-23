"""
SQL Repair Agent
───────────────────────────────────────────────────────────────────────────────
This agent is part of the Data Collection SequentialAgent pipeline.

Purpose:
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

# data_analysis_agent/subagents/sql_repair_agent/agent.py
from __future__ import annotations
from typing import AsyncGenerator, Any

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from pydantic import PrivateAttr


class SqlRepairAgent(BaseAgent):
    _generator: Any = PrivateAttr()
    _validator: Any = PrivateAttr()

    def __init__(self) -> None:
        super().__init__(
            name="SqlRepairAgent",
            description="Regenerates SQL if the validator reports a failure.",
        )
        # Lazy imports to avoid circular refs
        from ..sql_generator_agent.agent import sql_generator_agent
        from ..sql_validator_agent.agent import sql_validator_agent

        self._generator = sql_generator_agent
        self._validator = sql_validator_agent

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state                     # ✅ correct attr

        validation_status: str = state.get("validation_status", "")
        if validation_status.startswith("valid"):
            return                                    # nothing to do

        bad_sql = state.get("sql_query", "")
        user_request = state.get("user_request", "")
        if not bad_sql or not user_request:
            yield Event(
                author=self.name,
                content=dict(parts=[dict(text="missing sql_query or user_request")])
            )
            return

        retry_prompt = f"""
            The following SQL was invalid:

            sql:
            {bad_sql}
            Validator said:
            {validation_status}

            Please regenerate a correct BigQuery SQL statement that fulfils: "{user_request}"
            Return only SQL, no commentary.
            """
        async for _ in self._generator.run_async(
            InvocationContext(
                session=ctx.session,
                prompt=retry_prompt,
            )
        ):
            pass  # _generator already stores result in state

        new_sql = state.get("sql_query", "").strip()
        if not new_sql:
            yield Event(
                author=self.name,
                content=dict(parts=[dict(text="⚠️ regeneration produced empty SQL")])
            )
            return

        # Validate again
        async for _ in self._validator.run_async(ctx):
            pass

        yield Event(
            author=self.name,
            content=dict(parts=[dict(text="🔄 SQL regenerated & re-validated")])
        )

sql_repair_agent = SqlRepairAgent()