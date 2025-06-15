from google.adk.agents import LlmAgent
from pydantic import BaseModel
from typing import List, Dict
import os
from dotenv import load_dotenv
from pathlib import Path
from google.adk.tools import FunctionTool

# ─── Load environment ───────────────────────────────────────
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)
FAST_LLM_MODEL = os.getenv("FAST_LLM_MODEL")
GEMINI_MODEL = "gemini-2.0-flash"
# ─── Tool: Read all schema files using relative path ───────
def read_all_schema_texts() -> str:
    """
    Reads all .txt schema files from the 'configs' folder,
    concatenates them into one raw string.
    """

    print(Path(__file__).resolve().parents[3] / "configs")  # should print real folder
    print((Path(__file__).resolve().parents[3] / "configs").glob("*.txt"))
    base_dir = Path(__file__).resolve().parents[3]
    print(base_dir)
    schema_dir = base_dir / "configs"
    contents = []
    for path in schema_dir.glob("*.txt"):
        with open(path, "r", encoding="utf-8") as f:
            contents.append(f.read())
    return "\n\n".join(contents)

schema_tool = FunctionTool(
    func=read_all_schema_texts
)

# ─── Structured Output Schema ────────────────────────────────
class AvailabilityOutput(BaseModel):
    available: str
    user_query: str
    raw_schema_text: str

# ─── LLM Agent Definition ───────────────────────────────────
data_availability_agent = LlmAgent(
    name="DataAvailabilityAgent",
    description=(
        "Checks whether a user's natural-language query can be answered using "
        "tables/fields defined across multiple .txt schema files in configs/."
    ),
    model=GEMINI_MODEL,
    tools=[schema_tool],
    instruction="""
    You are the Data Availability Checker Agent.

    Instructions:
    1. Call `read_all_schema_texts()`.
    2. Parse the schema and check whether the user_query can be answered.
    3. Return a JSON-formatted string with the following structure:

    {
      "available": true/false,
      "user_query": "<same as input>",
      "raw_schema_text": "<entire schema text used>"
    }

    Guidelines:
    - Output must be valid JSON (do not include markdown or extra commentary).
    - If the query cannot be answered, set `"available": false` and still return the schema.
""",
    output_key="availability_result",
)
