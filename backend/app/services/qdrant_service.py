from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import Optional, List, Dict
import logging

class QdrantService:
    """
    Wrapper for Qdrant vector database operations.
    """

    def __init__(self):
        """
        Initialize Qdrant client.
        """
        self.client = QdrantClient("localhost", port=6333)
        self.collection_name = "documents"
        self.setup_collection()

    def setup_collection(self):
        """
        Set up the Qdrant collection if it doesn't exist.
        """
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
            )

    def search(self, project_id: str, query: str, limit: int = 5) -> Optional[List[Dict]]:
        """
        Search for similar documents in Qdrant.

        Args:
            project_id: The project ID to filter by.
            query: The search query.
            limit: The maximum number of results to return.

        Returns:
            List of similar documents or None if no results.
        """
        try:
            # Simulate embedding generation (replace with actual embedding model)
            query_vector = [0.1] * 1536

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="project_id",
                            match=models.MatchValue(value=project_id),
                        )
                    ]
                ),
                limit=limit,
            )

            return [result.payload for result in results]

        except Exception as e:
            logging.error(f"Error searching Qdrant: {e}")
            return None
