from typing import List
from google.cloud import aiplatform
from .config import get_settings

_settings = get_settings()
aiplatform.init(project=_settings.project_id, location=_settings.region)

# Re-use the same client across calls
_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name=_settings.vertex_index_endpoint
)


def search(embedding: List[float], k: int = 3):
    """Return Matching Engine neighbors for a single embedding."""
    response = _endpoint.find_neighbors(
        deployed_index_id=_settings.vertex_deployed_index,
        queries=[embedding],
        num_neighbors=k,
    )
    return response[0].neighbors        # list of Neighbor objects
