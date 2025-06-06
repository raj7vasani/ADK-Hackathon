"""
Agent 1: Data Availability Agent
Description:
    This agent receives a natural language query and verifies whether the requested data exists
    in the connected BigQuery environment. It checks the availability of relevant tables, fields,
    or metrics and flags whether the downstream data retrieval is possible. If the data does not exist,
    it stops the pipeline and provides a structured explanation.
"""
