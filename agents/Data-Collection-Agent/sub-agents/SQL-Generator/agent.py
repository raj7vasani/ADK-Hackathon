"""
Agent 2: SQL Generation Agent
Description:
    This agent takes a validated natural language query and converts it into a corresponding
    SQL statement using a large language model (e.g., Gemini via Vertex AI). The SQL is optimized
    for execution on BigQuery and tailored to the data schema. It outputs the SQL string to be executed
    by the data retrieval component.
"""
