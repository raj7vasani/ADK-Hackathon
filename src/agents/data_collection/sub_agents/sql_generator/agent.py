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

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

# ──────────────────────────────────────────────────────────────────────────────
# Load model name from .env  (e.g., FAST_LLM_MODEL=gemini-1.5-flash)
# ──────────────────────────────────────────────────────────────────────────────
env_path = Path(__file__).resolve().parents[4] / ".env"  # adjust depth if needed
load_dotenv(dotenv_path=env_path)
FAST_LLM_MODEL = os.getenv("FAST_LLM_MODEL", "gemini-1.5-flash")

# ──────────────────────────────────────────────────────────────────────────────
# LLM-powered SQL Generator
# ──────────────────────────────────────────────────────────────────────────────
sql_generation_agent = LlmAgent(
    name="SQLGeneratorAgent",
    model=FAST_LLM_MODEL,
    description="Generates a BigQuery-compatible SQL query from natural language.",
    # The prompt sees {{user_request}} and {{table_context}} auto-injected
    instruction="""
You are an expert analytics engineer who writes **efficient BigQuery SQL**.

Your task:
1. Read the user's English request: {{user_request}}
2. Consult ONLY the available schema definitions: {{table_context}}
3. Produce a single, correct SQL statement for Google BigQuery.
   • Use fully-qualified table names when provided.
   • Alias tables & columns clearly.
   • Prefer CTEs for readability if multiple steps are needed.
   • Do NOT include back-ticks ``` or Markdown fencing.
   • Do NOT add explanations or comments—return only raw SQL.

Output format:
<SQL starts on first line>
SELECT ...
...
;  -- terminating semicolon optional
""",
    # LlmAgent will automatically save the final response text to this key
    output_key="sql_query",
)
