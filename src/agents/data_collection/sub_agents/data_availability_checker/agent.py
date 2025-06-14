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

# ─── Tool: Read all schema files using relative path ───────
def read_all_schema_texts() -> str:
    """
    Reads all .txt schema files from the 'configs' folder,
    concatenates them into one raw string.
    """
    base_dir = Path(__file__).resolve().parents[2]
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
    available: bool
    missing_tables: List[str]
    missing_fields: Dict[str, List[str]]
    explanation: str

# ─── LLM Agent Definition ───────────────────────────────────
data_availability_agent = LlmAgent(
    name="DataAvailabilityAgent",
    description=(
        "Checks whether a user's natural-language query can be answered using "
        "tables/fields defined across multiple .txt schema files in configs/."
    ),
    model=FAST_LLM_MODEL,
    tools=[schema_tool],
    instruction="""
    You are the Data Availability Agent.

    Inputs:
    - user_query (string)
    - tool output: raw_schema_text (all .txt files concatenated)

    Tasks:
    1. Parse raw_schema_text to extract table definitions and columns.
    2. Identify which tables/columns are implied by the user_query.
    3. Check availability against parsed metadata.
    4. Format your response as below syntax.
    Output Format:
    
        available: true/false?,
        if available is false: return a to the user that message in short that query cannot be answered. 
        if available is true: return a message in short that query can be answered.
    
""",
    output_key="availability",
)
