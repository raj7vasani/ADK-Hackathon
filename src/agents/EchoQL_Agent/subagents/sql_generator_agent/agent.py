"""
SQL Generator Agent for EchoQL

This agent is responsible for generating BigQuery SQL queries from natural language user questions within the EchoQL agentic workflow.

Workflow Context:
- Step 3 in the EchoQL pipeline: Receives a user query and schema context after data availability has been checked.
- Utilizes a language model (LLM) to generate syntactically correct BigQuery SQL, referencing both the user request and relevant schema/documentation.
- Ensures all tables are fully qualified in the Mock_KPIs dataset and adheres strictly to GoogleSQL (Standard SQL) grammar.
- Returns only raw SQL (no markdown, comments, or prose).

Inputs:
- `availability_result`: JSON string from the Data Availability Checker, containing:
    - `user_query`: The original user question.
    - `raw_schema_text`: Schema context for the query.
    - `available`: Boolean indicating if the query can be answered.

Outputs:
- Emits an event with the generated SQL query, or an error message if generation is not possible.

This agent is designed to be robust, handling missing or malformed input gracefully, and always referencing the latest BigQuery SQL documentation for accuracy.
"""

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.genai import types

import json, os, re, requests, bs4
from pathlib import Path
from dotenv import load_dotenv

# Config
current_path = Path(__file__).resolve()
for parent in current_path.parents:
    env_file = parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

GEMINI_MODEL = os.getenv("FAST_LLM_MODEL", "gemini-1.5-flash")


# Utility: Event factory
def _make_event(author: str, text: str) -> Event:
    return Event(author=author, content=types.Content(parts=[types.Part(text=text)]))


# Helper: scrape GoogleSQL reference page
def fetch_bigquery_reference() -> str:
    """Return the first ~4 kB of the BigQuery Standard SQL syntax page as plain text."""
    url = (
        "https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax"
    )
    try:
        html = requests.get(url, timeout=15).text
        soup = bs4.BeautifulSoup(html, "html.parser")
        text = re.sub(r"\s+", " ", (soup.find("main") or soup).get_text(" ", strip=True))
        return text[:4000]  # keep prompt size reasonable
    except Exception as exc:  # never crash the agent run
        return f"[reference-fetch-failed → {exc}]"


# LLM agent that writes state["sql_query"]
_sql_llm = LlmAgent(
    name="SqlGeneratorLlm",
    model=GEMINI_MODEL,
    description="Generates BigQuery SQL.",
    instruction="""
    You are a BigQuery SQL generator.
    
    • Question: {{user_request}}
    • Schema  : {{table_context}}
    • Docs    : {{reference_docs}}
    
    INSTRUCTIONS:
    - All tables live in dataset Mock_KPIs – always fully-qualify (e.g. Mock_KPIs.sessions).
    - Use clear, self-documenting aliases (e.g. SELECT COUNT(*) as num_users FROM Mock_KPIs.mock_users 
        instead of SELECT COUNT(*) FROM mock_users ).
    - Obey GoogleSQL (Standard SQL) grammar exactly.
    - **Return raw SQL only** – no markdown, no comments, no prose.
    """,
    output_key="sql_query"
)


# Wrapper agent
class SqlGeneratorWrapper(BaseAgent):
    name: str = "SqlGeneratorAgent"
    description: str = (
        "Parses availability_result, fetches GoogleSQL docs, then calls the SQL LLM."
    )

    async def _run_async_impl(self, ctx: InvocationContext):
        st = ctx.session.state

        # 1) Parse availability_result emitted by the checker agent
        raw = st.get("availability_result", "").strip()
        raw = re.sub(r'^\s*```(?:json)?', "", raw)
        raw = re.sub(r'\s*```$', "", raw).strip()

        if not raw:
            yield _make_event(self.name, "❌ availability_result missing.")
            return

        try:
            avail = json.loads(raw)
        except json.JSONDecodeError as exc:
            yield _make_event(self.name, f"❌ JSON parse error: {exc}")
            return

        if not avail.get("available"):
            yield _make_event(
                self.name, "❌ Query cannot be answered with current schema."
            )
            return

        # 2) Inject prompt variables for the LLM
        st["user_request"] = avail["user_query"]
        st["table_context"] = avail["raw_schema_text"]
        st["reference_docs"] = fetch_bigquery_reference()

        # 3) Delegate to the LLM agent
        async for ev in _sql_llm.run_async(ctx):
            yield ev


# Export instance expected by ADK loader
sql_generator_agent = SqlGeneratorWrapper()
