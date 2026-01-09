"""
Qdrant Vector Database Service for GravityWork

This service provides a wrapper around Qdrant for:
- Creating and managing collections
- Storing and retrieving document embeddings
- Performing vector similarity searches
"""

import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse

class QdrantService:
    """
    Wrapper service for Qdrant vector database operations.
    """

    def __init__(self, host: str = None, port: int = None):
        """
        Initialize Qdrant client.

        Args:
            host: Qdrant server host (defaults to QDRANT_HOST env var)
            port: Qdrant server port (defaults to QDRANT_PORT env var or 6333)
        """
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.client = QdrantClient(host=self.host, port=self.port)

    def create_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,
        distance_metric: str = "Cosine"
    ) -> bool:
        """
        Create a new collection in Qdrant.

        Args:
            collection_name: Name of the collection to create
            vector_size: Size of the vectors to be stored
            distance_metric: Distance metric to use (Cosine, Euclidean, Dot)

        Returns:
            bool: True if collection was created, False if it already exists
        """
        try:
            # Check if collection already exists
            if self.collection_exists(collection_name):
                return False

            # Create the collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance(distance_metric)
                )
            )
            return True
        except Exception as e:
            print(f"Error creating collection {collection_name}: {e}")
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
            self.client.get_collection(collection_name)
            return True
        except UnexpectedResponse:
            return False

    def upsert_vectors(
        self,
        collection_name: str,
        vectors: List[Dict[str, Any]]
    ) -> bool:
        """
        Upsert vectors into a collection.

        Args:
            collection_name: Name of the collection
            vectors: List of vectors with their metadata

        Returns:
            bool: True if upsert was successful
        """
        try:
            # Prepare points for upsert
            points = []
            for vector in vectors:
                point = qdrant_models.PointStruct(
                    id=vector.get("id"),
                    vector=vector["vector"],
                    payload=vector.get("metadata", {})
                )
                points.append(point)

            # Perform upsert
            self.client.upsert(
                collection_name=collection_name,
                points=points,
                wait=True
            )
            return True
        except Exception as e:
            print(f"Error upserting vectors: {e}")
            return False

    def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in a collection.

        Args:
            collection_name: Name of the collection to search
            query_vector: Query vector for similarity search
            limit: Maximum number of results to return
            filters: Optional filters for metadata

        Returns:
            List of search results with scores and payloads
        """
        try:
            # Convert filters if provided
            qdrant_filters = None
            if filters:
                qdrant_filters = self._convert_filters(filters)

            # Perform search
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=qdrant_filters
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                })

            return formatted_results
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []

    def _convert_filters(self, filters: Dict) -> qdrant_models.Filter:
        """
        Convert dictionary filters to Qdrant Filter object.

        Args:
            filters: Dictionary of filter conditions

        Returns:
            Qdrant Filter object
        """
        conditions = []
        for field, value in filters.items():
            if isinstance(value, dict):
                # Handle range queries
                if "min" in value and "max" in value:
                    conditions.append(
                        qdrant_models.FieldCondition(
                            key=field,
                            range=qdrant_models.Range(
                                gte=value["min"],
                                lte=value["max"]
                            )
                        )
                    )
                # Handle exact match
                elif "eq" in value:
                    conditions.append(
                        qdrant_models.FieldCondition(
                            key=field,
                            match=qdrant_models.MatchValue(value=value["eq"])
                        )
                    )
            else:
                # Simple exact match
                conditions.append(
                    qdrant_models.FieldCondition(
                        key=field,
                        match=qdrant_models.MatchValue(value=value)
                    )
                )

        if len(conditions) == 1:
            return qdrant_models.Filter(must=conditions)
        else:
            return qdrant_models.Filter(must=conditions)

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection information
        """
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "config": info.config
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {}

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.

        Args:
            collection_name: Name of the collection to delete

        Returns:
            bool: True if deletion was successful
        """
        try:
            self.client.delete_collection(collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
