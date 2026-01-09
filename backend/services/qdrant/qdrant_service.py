import logging
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse
import os

logger = logging.getLogger(__name__)

class QdrantService:
    """
    Qdrant vector database service wrapper.
    Handles connection, collection management, and basic CRUD operations.
    """

    def __init__(self, url: Optional[str] = None):
        """
        Initialize Qdrant client.

        Args:
            url: Qdrant server URL. If None, uses QDRANT_URL from environment.
        """
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.client = QdrantClient(url=self.url)
        logger.info(f"Qdrant client initialized with URL: {self.url}")

    def create_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,
        distance: str = "Cosine",
        **kwargs
    ) -> bool:
        """
        Create a new collection in Qdrant.

        Args:
            collection_name: Name of the collection
            vector_size: Size of the vectors to be stored
            distance: Distance metric to use (Cosine, Euclidean, Dot)
            **kwargs: Additional collection parameters

        Returns:
            bool: True if collection was created or already exists
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            if any(c.name == collection_name for c in collections.collections):
                logger.info(f"Collection {collection_name} already exists")
                return True

            # Create new collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=vector_size,
                    distance=qdrant_models.Distance(distance.upper())
                ),
                **kwargs
            )
            logger.info(f"Created collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {str(e)}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists.

        Args:
            collection_name: Name of the collection to check

        Returns:
            bool: True if collection exists
        """
        try:
            collections = self.client.get_collections()
            return any(c.name == collection_name for c in collections.collections)
        except Exception as e:
            logger.error(f"Error checking collection existence: {str(e)}")
            return False

    def upsert_vectors(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> bool:
        """
        Upsert vectors into a collection.

        Args:
            collection_name: Target collection name
            vectors: List of vectors to upsert (each should have 'id', 'vector', and optional 'payload')
            batch_size: Batch size for upsert operations

        Returns:
            bool: True if upsert was successful
        """
        try:
            if not self.collection_exists(collection_name):
                logger.error(f"Collection {collection_name} does not exist")
                return False

            # Process vectors in batches
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                points = [
                    qdrant_models.PointStruct(
                        id=vector["id"],
                        vector=vector["vector"],
                        payload=vector.get("payload", {})
                    )
                    for vector in batch
                ]

                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )

            logger.info(f"Upserted {len(vectors)} vectors into {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {str(e)}")
            return False

    def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar vectors in a collection.

        Args:
            collection_name: Collection to search in
            query_vector: Query vector
            limit: Maximum number of results to return
            filters: Optional search filters

        Returns:
            List of search results with scores and payloads
        """
        try:
            if not self.collection_exists(collection_name):
                logger.error(f"Collection {collection_name} does not exist")
                return []

            search_result = self.client.search(
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
                for result in search_result
            ]
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.

        Args:
            collection_name: Name of the collection to delete

        Returns:
            bool: True if deletion was successful
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            return False

    def get_collection_info(self, collection_name: str) -> Optional[Dict]:
        """
        Get information about a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection info or None if not found
        """
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.points_count,
                "config": info.config
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return None
