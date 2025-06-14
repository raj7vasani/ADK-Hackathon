from pathlib import Path
from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # ── Core GCP ────────────────────────────────────────────────────────────────
    project_id: str = Field(..., env="GOOGLE_CLOUD_PROJECT")
    region: str = Field("europe-west3", env="GOOGLE_CLOUD_LOCATION")

    # ── Vector Search resources (fill from .env) ───────────────────────────────
    vertex_index_endpoint: str = Field(env="VERTEX_INDEX_ENDPOINT_ID")
    vertex_deployed_index: str = Field(env="VERTEX_DEPLOYED_INDEX_ID")

    # ── Models ────────────────────────────────────────────────────────────────
    embedding_model: str = Field(env="EMBEDDING_MODEL")
    embedding_dim: int = Field(env="EMBEDDING_DIM")
    llm_model: str = Field(env="FAST_LLM_MODEL")

    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:        # singleton accessor
    return Settings()
