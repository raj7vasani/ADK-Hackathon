from typing import List
import vertexai
from vertexai.preview.language_models import TextEmbeddingModel
from .config import get_settings

_settings = get_settings()
vertexai.init(project=_settings.project_id, location=_settings.region)

_model: TextEmbeddingModel | None = None


def _load_model() -> TextEmbeddingModel:
    global _model
    if _model is None:
        _model = TextEmbeddingModel.from_pretrained(_settings.embedding_model)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Returns a list of 768-dim embeddings (one per input string)."""
    model = _load_model()
    return [e.values for e in model.get_embeddings(texts)]
