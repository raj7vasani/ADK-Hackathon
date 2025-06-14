"""
Agent 4: BigQuery Fetcher Agent
───────────────────────────────────────────────────────────────────────────────
• Expects a VALIDATED BigQuery SQL query to be present in session.state
  under the key ``"sql_query"`` **and** the key ``"validation_status"`` to
  equal ``"valid"`` (set by the SQL-Validator agent).

• Executes the query with ``fetch_data`` (wrapper around
  google.cloud.bigquery.Client.query).

• Saves the resulting DataFrame both:
    1.  Into ``session.state["query_result_df"]``        (lightweight use by
        downstream agents if needed, *not* sent to the user UI), and
    2.  As a CSV artifact called ``query_result.csv`` so the ADK UI turns it
        into a **download button** for the end-user.

• Emits an ``Event`` summarising row count + download hint.

If the query hasn’t been validated this agent quietly exits, letting the
SequentialAgent continue / eventually surface the earlier validation error.
"""

from __future__ import annotations

import io
from typing import AsyncGenerator

import pandas as pd
from google.genai import types  # Part representation used for artifacts

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from src.connectors.bigquery_connector import fetch_data


class BigQueryFetcherAgent(BaseAgent):
    name = "BigQueryFetcherAgent"
    description = "Runs a validated SQL query on BigQuery and returns the result as a downloadable CSV."

    # ──────────────────────────────────────────────────────────────────────────
    # Core async implementation
    # ──────────────────────────────────────────────────────────────────────────

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # ------------------------------------------------------------------ #
        # 1) Guard-checks – only act if previous agent marked SQL as valid
        # ------------------------------------------------------------------ #
        state = ctx.session.state
        sql_query: str | None = state.get("sql_query")
        validation_status: str | None = state.get("validation_status")

        if sql_query is None or validation_status != "valid":
            # Nothing to do – either the query is missing or wasn’t valid.
            return

        # ------------------------------------------------------------------ #
        # 2) Execute the query
        # ------------------------------------------------------------------ #
        try:
            df: pd.DataFrame = fetch_data(sql_query)
        except Exception as exc:  # pragma: no cover
            # Surface DB/runtime errors back to the user
            err_msg = f"❌ BigQuery execution failed: {exc}"
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=types.Content(parts=[types.Part.from_text(err_msg)]),
            )
            return

        # Keep a lightweight copy in session.state for any sibling agent
        state["query_result_df"] = df

        # ------------------------------------------------------------------ #
        # 3) Persist as CSV artifact so UI shows a “Download” link
        # ------------------------------------------------------------------ #
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue()

        # build google.genai Part (ADK’s standard binary holder)
        csv_part = types.Part.from_bytes(
            data=csv_bytes, mime_type="text/csv"
        )

        # ctx.save_artifact() returns the new version id – not needed further
        ctx.save_artifact(filename="query_result.csv", artifact=csv_part)

        # ------------------------------------------------------------------ #
        # 4) Emit a summary Event so the user sees something in the chat
        # ------------------------------------------------------------------ #
        success_msg = (
            f"✅ Query executed successfully – **{len(df):,} rows** returned.\n\n"
            "Click the *Download* button above to save the CSV."
        )
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=types.Content(parts=[types.Part.from_text(success_msg)]),
        )
