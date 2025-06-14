"""
Sequential Agent for Data Collection
"""

from google.adk.agents import SequentialAgent

from .sub_agents.data_availability_checker.agent import data_availability_agent
from .sub_agents.sql_generator.agent import sql_generation_agent
from .sub_agents.sql_validator.agent import sql_validator_agent

root_agent = SequentialAgent(
    name="Data Collection Agent",
    sub_agents=[data_availability_agent, sql_generation_agent, sql_validation_agent],
    description="This agent orchestrates the data collection process by checking data availability, generating SQL queries, and validating them before execution.",
)