"""
This script generates a JSON schema catalog for a BigQuery dataset.
"""
from google.cloud import bigquery
import json
from collections import defaultdict

def generate_schema(project_id: str, dataset_id: str, output_file: str = "../configs/schema.json"):
    client = bigquery.Client(project=project_id)

    # Get table descriptions
    tables_query = f"""
        SELECT table_name, table_type
        FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
    """
    tables = client.query(tables_query).result()

    # Get column metadata
    columns_query = f"""
        SELECT table_name, column_name, data_type
        FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    """
    columns = client.query(columns_query).result()

    schema = defaultdict(lambda: {"description": "", "columns": {}})

    for row in tables:
        schema[row.table_name]["description"] = f"{row.table_type} in {dataset_id}"

    for row in columns:
        schema[row.table_name]["columns"][row.column_name] = row.data_type

    output = {"tables": dict(schema)}

    # Write to JSON
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Schema metadata saved to {output_file}")

# Example usage:
generate_schema("adk-hackathon-461216", "Mock_KPIs")
