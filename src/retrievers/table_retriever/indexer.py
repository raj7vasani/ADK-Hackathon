import json, uuid, pathlib, argparse, asyncio
from google.cloud import storage, aiplatform
from .config import get_settings
from .embedder import embed_texts

settings = get_settings()

def build_jsonl(schemas: dict[str, str], outfile: str):
    embeddings = embed_texts(list(schemas.values()))
    with open(outfile, "w") as f:
        for (tbl, text), emb in zip(schemas.items(), embeddings):
            rec = {"id": tbl, "embedding": emb, "table_name": tbl, "text": text}
            f.write(json.dumps(rec) + "\n")

def upload_to_gcs(local_path: str, gcs_dir: str):
    client = storage.Client()
    bucket = client.bucket(settings.gcs_bucket)
    blob = bucket.blob(f"{gcs_dir}/{pathlib.Path(local_path).name}")
    blob.upload_from_filename(local_path)

def create_index(gcs_uri: str):
    idx = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=f"tables-{uuid.uuid4().hex[:8]}",
        contents_delta_uri=gcs_uri,
        dimensions=settings.embedding_dim,
        distance_measure_type="DOT_PRODUCT_DISTANCE",
        index_update_method="STREAM_UPDATE",
    )
    idx.wait()
    return idx

def deploy_index(idx):
    ep = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=f"{idx.display_name}-ep", public_endpoint_enabled=True
    )
    ep.deploy_index(index=idx, deployed_index_id=f"di-{uuid.uuid4().hex[:6]}")
    return ep

# CLI omitted for brevity
