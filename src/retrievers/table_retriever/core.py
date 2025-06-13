from typing import List, Tuple
from vertexai.preview.language_models import TextGenerationModel

from .embedder import embed_texts
from .vector_store import search
from .config import get_settings

_settings = get_settings()


class TableRetrieverAgent:
    """LLM-enriches a user query, embeds it, and fetches the top-K table IDs by performing a semantic search."""

    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self._llm = TextGenerationModel.from_pretrained(_settings.llm_model)

    # ── public interface ────────────────────────────────────────────────────
    def __call__(self, user_query: str) -> Tuple[str, List[str]]:
        detailed_query = self._enrich_query(user_query)
        embedding = embed_texts([detailed_query])[0]
        tables = self._retrieve_tables(embedding)
        return detailed_query, tables

    # ── helpers ────────────────────────────────────────────────────────────
    def _enrich_query(self, user_query: str) -> str:
        prompt = (
            "Rewrite the following short user query into a detailed data-analysis "
            "request. Clarify goals, metrics, filters, and time windows.\n\n"
            f"User query: {user_query}\n"
            "Detailed request:"
        )
        resp = self._llm.predict(prompt, max_output_tokens=256)
        return resp.text.strip()

    def _retrieve_tables(self, embedding: List[float]) -> List[str]:
        neighbors = search(embedding, k=self.top_k)
        return [n.id for n in neighbors]
