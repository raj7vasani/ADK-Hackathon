"""Pre-pipeline router that:
   1. Runs TableRetriever utility
   2. Calls ADK sequential pipeline
"""
from typing import Dict, Any
from src.retrievers.table_retriever import TableRetriever
from data_collection.sub_agents import run_pipeline  # adjust path if your agent object differs

table_retriever = TableRetriever(top_k=3)

def handle_user_query(raw_query: str) -> Dict[str, Any]:
    detailed, tables = table_retriever(raw_query)

    payload = {
        "query": detailed,
        "tables": tables,
    }
    return run_pipeline(payload)
