"""
Agent 2: SQL Generation Agent
───────────────────────────────────────────────────────────────────────────────
Role
----
Converts an English analytics request into a BigQuery-compatible SQL statement
that can be fed to downstream validators and executors.

Assumptions
-----------
Downstream steps expect the SQL string under session.state["sql_query"].
Upstream agents place the following keys in session.state:

* user_request      – original NL question from the user (str)
* table_context     – relevant table / column definitions as plain text (str)

Output
------
* Writes the generated SQL (no Markdown fencing) to session.state["sql_query"]
  via the `output_key` convenience parameter.

Usage
-----
Simply import `sql_generation_agent` in your root pipeline; no wrapper code
required.
"""

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event                    # <-- use this
from google.genai import types                               # for Content/Part
import json, os
from pathlib import Path
from dotenv import load_dotenv

# ─── Config ──────────────────────────────────────────────────
env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(env_path)
MODEL = os.getenv("FAST_LLM_MODEL", "gemini-2.0-flash")

# ─── Pure LLM agent that writes state["sql_query"] ───────────
_sql_llm = LlmAgent(
    name="SQLGeneratorLlm",
    model=MODEL,
    description="Generates BigQuery SQL.",
    instruction="""
You are a BigQuery SQL generator.
• Question: {{user_request}}
• Schema : {{table_context}}
Return raw SQL only (no markdown, no comments).
""",
    output_key="sql_query",
)

# ─── Helper to create a text-only Event ──────────────────────
def make_msg(author: str, text: str) -> Event:
    return Event(
        author=author,
        content=types.Content(parts=[types.Part(text=text)]),
    )

# ─── Wrapper agent ───────────────────────────────────────────
class SQLGeneratorWrapper(BaseAgent):
    name: str = "SQLGeneratorAgent"
    description: str = "Parses availability_result and calls the SQL LLM."

    async def _run_async_impl(self, ctx: InvocationContext):
        st = ctx.session.state

        raw = st.get("availability_result", "")
        if not raw:
            yield make_msg(self.name, "❌ availability_result missing")
            return

        raw = raw.strip("`").strip()
        try:
            avail = json.loads(raw)
        except json.JSONDecodeError as e:
            yield make_msg(self.name, f"❌ JSON parse error: {e}")
            return

        if not avail.get("available", False):
            yield make_msg(self.name, "❌ Query cannot be answered with current schema.")
            return

        # push data for the LLM prompt
        st["user_request"]  = avail["user_query"]
        st["table_context"] = avail["raw_schema_text"]

        # delegate to the LLM agent
        async for ev in _sql_llm.run_async(ctx):
            yield ev


# exported instance
sql_generation_agent = SQLGeneratorWrapper()