"""
This is a script to upload CSV files from a local directory to Google BigQuery.
"""

import os
from google.cloud import bigquery

# === CONFIG ===
PROJECT_ID = "adk-hackathon-461216"
DATASET_ID = "Mock_KPIs"
DATA_FOLDER = "../Mock_Data"  # relative to this script

# === INIT BIGQUERY CLIENT ===
client = bigquery.Client(project=PROJECT_ID)

def upload_csv_to_bigquery(csv_file_path, table_name):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_TRUNCATE",  # Overwrites if table exists
    )

    with open(csv_file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)

    job.result()  # Wait for the job to complete
    print(f"✅ Uploaded {csv_file_path} to {table_id}")

def main():
    abs_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), DATA_FOLDER))

    for file_name in os.listdir(abs_data_folder):
        if file_name.endswith(".csv"):
            table_name = file_name.replace(".csv", "")
            full_path = os.path.join(abs_data_folder, file_name)
            upload_csv_to_bigquery(full_path, table_name)

if __name__ == "__main__":
    main()
