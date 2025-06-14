"""
Agent 1: Data Collection Agent
───────────────────────────────────────────────────────────────────────────────
• Checks data availability
• Generates SQL
• Validates SQL
• Executes SQL
• Returns a CSV to the user
"""
from google.adk.agents import SequentialAgent

from .sub_agents.data_availability_checker.agent import data_availability_agent
from .sub_agents.sql_generator.agent import sql_generation_agent
from .sub_agents.sql_validator.agent import sql_validator_llm
from .sub_agents.sql_fetcher.agent import BigQueryFetcherAgent

sql_fetcher_agent = BigQueryFetcherAgent()

root_agent = SequentialAgent(
    name="DataCollectionAgent",
    description=(
        "Checks data availability, generates SQL, validates it, "
        "executes the query, and returns a CSV to the user."
    ),
    sub_agents=[
        data_availability_agent,
        sql_generation_agent,            # adds sql_query + user_request
        sql_validator_llm,               # adds validation_status
        sql_fetcher_agent,          # consumes above and attaches CSV
    ],
)
