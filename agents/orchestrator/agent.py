"""
Orchestrator Agent
Description:
This agent is responsible for managing and coordinating the sequential execution of the
multi-agent data analysis pipeline. It receives a natural language query from the end user
or external client and routes it through the following agents in order:

1. Data Availability Agent – checks whether the requested data exists in the system.
2. SQL Generation Agent – transforms the validated query into an executable SQL statement.
3. SQL Validator Agent – validates the generated SQL for syntax and semantic correctness.

The Orchestrator Agent handles all inter-agent communication, error propagation, and recovery
logic. It ensures that fallback or retry mechanisms are triggered when an agent fails or
produces invalid output, enabling robustness across the end-to-end workflow.

This agent serves as the main entrypoint for the overall agentic system and is designed to be
stateless, modular, and extensible for additional workflows or parallel agent branches.
"""