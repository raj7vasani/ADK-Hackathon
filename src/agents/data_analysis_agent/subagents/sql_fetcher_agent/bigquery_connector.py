import os
import pandas as pd
from google.cloud import bigquery

# 1) Your GCP project ID
GCP_PROJECT_ID = "adk-hackathon-461216"

# 2) (Optional) If you are not using Application Default Credentials,
#    uncomment and set the path to your service-account JSON file:
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your-key.json"

# ──────────────────────────────────────────────────────────────────────────────
# INITIALIZE BIGQUERY CLIENT
# ──────────────────────────────────────────────────────────────────────────────

bq_client = bigquery.Client(project=GCP_PROJECT_ID)


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC FUNCTION
# ──────────────────────────────────────────────────────────────────────────────

def fetch_data(sql_query: str) -> pd.DataFrame:
    """
    Execute the given SQL query on BigQuery and return the results as a pandas DataFrame.

    Args:
        sql_query (str): A fully-qualified BigQuery SQL query string.

    Returns:
        pd.DataFrame: The result rows as a DataFrame.
    """
    query_job = bq_client.query(sql_query)
    dataframe = query_job.result().to_dataframe()
    return dataframe
