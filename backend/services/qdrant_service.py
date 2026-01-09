from typing import List, Dict, Optional
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as qdrant_models
import logging

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self, host: str = "qdrant", port: int = 6333, api_key: Optional[str] = None):
        self.client = QdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            timeout=30.0
        )

    def create_collection(self, collection_name: str, vector_size: int = 1536):
        """Create a new collection in Qdrant."""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=vector_size,
                    distance=qdrant_models.Distance.COSINE
                )
            )
            logger.info(f"Collection '{collection_name}' created successfully.")
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}")
            raise

    def insert_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """Insert vectors into a collection."""
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=qdrant_models.Batch(
                    ids=ids or [None] * len(vectors),
                    vectors=vectors,
                    payloads=payloads
                )
            )
            logger.info(f"Inserted {len(vectors)} vectors into '{collection_name}'.")
        except Exception as e:
            logger.error(f"Failed to insert vectors into '{collection_name}': {e}")
            raise

    def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar vectors in a collection."""
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filters
            )
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Failed to search vectors in '{collection_name}': {e}")
            raise

    def get_collection_info(self, collection_name: str) -> Dict:
        """Get information about a collection."""
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.points_count,
                "config": info.config
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for '{collection_name}': {e}")
            raise
