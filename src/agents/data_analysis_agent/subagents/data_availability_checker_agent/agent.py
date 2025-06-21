from google.adk.agents import LlmAgent
from pydantic import BaseModel
from typing import List, Dict
import os
from dotenv import load_dotenv
from pathlib import Path
from google.adk.tools import FunctionTool

current_path = Path(__file__).resolve()
for parent in current_path.parents:
    env_file = parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

FAST_LLM_MODEL = os.getenv("FAST_LLM_MODEL")
GEMINI_MODEL = "gemini-2.0-flash"


# ─── LLM Agent Definition ───────────────────────────────────
data_availability_checker_agent = LlmAgent(
    name="DataAvailabilityCheckerAgent",
    description=(
        "Checks whether a user's natural-language query can be answered using the available tables and fields in the database."
    ),
    model=GEMINI_MODEL,
    instruction="""
    You are the Data Availability Checker Agent.

    These are the available tables and fields in the database:
    
    Table: mock_answers
    Description: Contains user-submitted answers to questions on the QA platform. Each answer is linked to a question and a user, and has a timestamp and textual content.
    Columns:
    - id: Unique identifier for the answer (INT64)
    - question_id: Foreign key to the associated question (INT64)
    - user_id: Foreign key to the user who answered (INT64)
    - created_at: Timestamp when the answer was submitted (TIMESTAMP)
    - content: Text content of the user's answer (STRING)

    Table: mock_questions
    Description: Stores user-generated questions posted on the platform. Each question is associated with a user and includes a timestamp and content.
    Columns:
    - question_id: Unique identifier for the question (INT64)
    - user_id: ID of the user who posted the question (INT64)
    - created_at: When the question was posted (TIMESTAMP)
    - content: The text of the question (STRING)

    Table: mock_users
    Description: Contains user profiles for the QA platform. Each user has a unique ID, name, email, and birthday.
    Columns:
    - id: Unique identifier for the user (INT64)
    - name: User's full name (STRING)
    - email: User's email address (STRING)
    - birthday: User's date of birth (DATE)

    Table: mock_user_sessions
    Description: Tracks user session activity such as session duration and date. Useful for engagement analysis and retention metrics.
    Columns:
    - session_id: Unique identifier for a user session (STRING)
    - user_id: ID of the user who had the session (INT64)
    - duration_min: Length of the session in minutes (FLOAT64)
    - session_date: Date on which the session occurred (DATE)

    Instructions:
    1. Parse the schema and check whether the user_query can be answered.
    2. Return a JSON-formatted string with the following structure:

    {
      "available": true/false,
      "user_query": "<same as input>",
      "raw_schema_text": "<entire schema text used>"
    }

    Guidelines:
    - Output must be **bare JSON** 
    – absolutely no ``` fences, no language tags, no extra commentary. 
    - Returning anything else will break downstream parsing.
    - If the query cannot be answered, set `"available": false and still return the schema.
""",
    output_key="availability_result",
)
