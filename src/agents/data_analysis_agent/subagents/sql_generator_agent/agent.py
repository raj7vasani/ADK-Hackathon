from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.genai import types
import json, os, re
from pathlib import Path
from dotenv import load_dotenv

# ─── Config ──────────────────────────────────────────────────
current_path = Path(__file__).resolve()
for parent in current_path.parents:
    env_file = parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break
FAST_LLM_MODEL = os.getenv("FAST_LLM_MODEL")
GEMINI_MODEL = "gemini-2.0-flash"


# ─── Pure LLM agent that writes state["sql_query"] ───────────
_sql_llm = LlmAgent(
    name="SqlGeneratorLlm",
    model=GEMINI_MODEL,
    description="Generates BigQuery SQL.",
    instruction="""
You are a BigQuery SQL generator.
• Question: {{user_request}}
• Schema : {{table_context}}
All tables live in dataset `Mock_KPIs`. **Always qualify tables**: e.g. `Mock_KPIs.<table_name>`
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
class SqlGeneratorWrapper(BaseAgent):
    name: str = "SqlGeneratorAgent"
    description: str = "Parses availability_result and calls the SQL LLM."

    async def _run_async_impl(self, ctx: InvocationContext):
        st = ctx.session.state

        raw = st.get("availability_result", "").strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw).strip()

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
sql_generator_agent = SqlGeneratorWrapper()