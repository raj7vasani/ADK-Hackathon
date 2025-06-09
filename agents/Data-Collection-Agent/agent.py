"""
Sequential Agent for Data Collection
"""

from google.adk.agents import SequentialAgent

from .subagents.Data-Availability-Checker import data_availability_agent
from .subagents.SQL-Generator import sql_generation_agent
from .subagents.SQL-Validator import sql_validation_agent

root_agent = SequentialAgent(
    name="Data Collection Agent",
    sub_agents=[data_availability_agent, sql_generation_agent, sql_validation_agent],
    description="This agent orchestrates the data collection process by checking data availability, generating SQL queries, and validating them before execution.",
)