import os
import sys
from pathlib import Path

# Add the project root directory to Python path BEFORE any src imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from typing import List
import json
from google.cloud import storage
from google.cloud import aiplatform
from sentence_transformers import SentenceTransformer
from src.retrievers.table_retriever.config import get_settings

# Get settings from .env file
settings = get_settings()

# Initialize the embedding model
model = SentenceTransformer(settings.embedding_model)

# Initialize GCS client
storage_client = storage.Client(project=settings.project_id)
bucket_name = settings.vertex_index_endpoint.split('/')[-1]  # Extract bucket name from endpoint
bucket = storage_client.bucket(bucket_name)

# Schema files to process
SCHEMA_FILES = [
    "mock_answers_description.txt",
    "mock_questions_description.txt",
    "mock_user_sessions_description.txt",
    "mock_users_description.txt"
]

def read_schema_file(file_path: str) -> str:
    """Read the content of a schema file."""
    with open(file_path, 'r') as f:
        return f.read()

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for the given text."""
    return model.encode(text).tolist()

def check_file_exists_in_bucket(file_name: str) -> bool:
    """Check if the embedded file already exists in the bucket."""
    blob = bucket.blob(f"schema_embeddings/{file_name}.json")
    return blob.exists()

def upload_embedding_to_bucket(file_name: str, embedding: List[float], original_text: str):
    """Upload the embedding to GCS bucket."""
    data = {
        "file_name": file_name,
        "embedding": embedding,
        "original_text": original_text
    }
    
    blob = bucket.blob(f"schema_embeddings/{file_name}.json")
    blob.upload_from_string(
        json.dumps(data),
        content_type='application/json'
    )

def main():
    config_dir = project_root / "configs"
    
    for schema_file in SCHEMA_FILES:
        file_path = config_dir / schema_file
        
        # Check if embedding already exists
        if check_file_exists_in_bucket(schema_file):
            print(f"Embedding for {schema_file} already exists in bucket. Skipping...")
            continue
        
        print(f"Processing {schema_file}...")
        
        # Read and embed the schema
        schema_text = read_schema_file(file_path)
        embedding = generate_embedding(schema_text)
        
        # Upload to bucket
        upload_embedding_to_bucket(schema_file, embedding, schema_text)
        print(f"Successfully uploaded embedding for {schema_file}")

if __name__ == "__main__":
    main() 