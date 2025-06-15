"""
Agent 4 – BigQuery Fetcher  (print-only version)
──────────────────────────────────────────────────────────────────────────────
• Expects in session.state
      sql_query         – cleaned & ready for BigQuery
      validation_status – must equal "valid"  (case-insensitive)

• Runs the query via src.connectors.bigquery_connector.fetch_data()

• Stores the DataFrame in session.state["query_result_df"] for any
  downstream agents, **and prints the DataFrame to the chat**.
"""

from __future__ import annotations

import re
from typing import AsyncGenerator

import pandas as pd
from google.genai import types

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from src.connectors.bigquery_connector import fetch_data


class BigQueryFetcherAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="BigQueryFetcherAgent",
            description="Executes validated SQL and prints the resulting DataFrame.",
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state

        # 1️⃣ Guard-check
        sql_query: str | None = state.get("sql_query")
        validation_status: str = state.get("validation_status", "").strip().lower()
        if not sql_query or validation_status != "valid":
            return  # nothing to do

        # Remove ```sql fences``` if present
        sql_query = re.sub(r'^```sql\s*|\s*```$', '', sql_query.strip(), flags=re.I)

        # 2️⃣ Run the query
        try:
            df: pd.DataFrame = fetch_data(sql_query)
        except Exception as exc:
            err_msg = f"❌ BigQuery execution failed: {exc}"
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=types.Content(parts=[types.Part(text=err_msg)]),
            )
            return

        state["query_result_df"] = df  # keep for any sibling agents

        # 3️⃣ Emit the DataFrame to the chat
        table_text = df.to_string(index=False)
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=types.Content(parts=[
                types.Part(text=f"✅ Query returned **{len(df):,} rows**\n\n```\n{table_text}\n```")
            ]),
        )
