"""
This script generates LLM-friendly text descriptions for a BigQuery dataset schema.
"""
from google.cloud import bigquery

def generate_schema_text(project_id: str, dataset_id: str, output_file: str = "../configs/mock_user_sessions_description.txt"):
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

    # Organize metadata
    schema = {}
    for row in tables:
        schema[row.table_name] = {
            "description": f"{row.table_type} in {dataset_id}",
            "columns": []
        }

    for row in columns:
        if row.table_name in schema:
            schema[row.table_name]["columns"].append((row.column_name, row.data_type))

    # Format as plain text
    output_lines = []
    for table_name, data in schema.items():
        output_lines.append(f"Table: {table_name}")
        output_lines.append(f"Description: {data['description']}")
        output_lines.append("Columns:")
        for col_name, col_type in data["columns"]:
            output_lines.append(f"- {col_name}: {col_type}")
        output_lines.append("")  # Blank line between tables

    # Write to a text file
    with open(output_file, "w") as f:
        f.write("\n".join(output_lines))

    print(f"✅ Schema text saved to {output_file}")

# Example usage:
generate_schema_text("adk-hackathon-461216", "Mock_KPIs")
