"""
Root Agent
───────────────────────────────────────────────────────────────────────────────
• Checks data availability
• Generates SQL
• Validates SQL
• Executes SQL
• Returns a CSV to the user
"""
from google.adk.agents import SequentialAgent

from .subagents.data_availability_checker_agent.agent import data_availability_checker_agent
from .subagents.sql_generator_agent.agent import sql_generator_agent
from .subagents.sql_validator_agent.agent import sql_validator_agent
from .subagents.sql_fetcher_agent.agent import sql_fetcher_agent
from .subagents.sql_repair_agent.agent import sql_repair_agent


root_agent = SequentialAgent(
    name="EchoQL_Agent",
    description=(
        "Checks data availability, generates SQL, validates it, "
        "executes the query, and returns a CSV to the user."
    ),
    sub_agents=[
        data_availability_checker_agent,    # check data availability
        sql_generator_agent,                # adds sql_query + user_request
        sql_validator_agent,                # adds validation_status
        sql_repair_agent,                   # adds sql_query + user_request
        sql_fetcher_agent,                  # consumes above and attaches CSV
    ],
)
