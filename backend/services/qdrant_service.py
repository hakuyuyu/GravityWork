import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as qdrant_models
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    """Represents a chunk of a document with metadata"""
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class SearchResult(BaseModel):
    """Represents a search result"""
    text: str
    metadata: Dict[str, Any]
    score: float

class QdrantService:
    """Wrapper service for Qdrant vector database operations"""

    def __init__(self):
        """Initialize Qdrant client from environment variables"""
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

        self.client = QdrantClient(
            host=qdrant_host,
            port=qdrant_port,
            prefer_grpc=False
        )
        self.collection_name = "documents"

    def create_collection(self, vector_size: int = 768) -> bool:
        """Create a collection for document embeddings"""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=vector_size,
                    distance=qdrant_models.Distance.COSINE
                )
            )
            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False

    def collection_exists(self) -> bool:
        """Check if collection exists"""
        try:
            return self.client.collection_exists(self.collection_name)
        except Exception:
            return False

    def upsert_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Upsert document chunks into Qdrant"""
        if not chunks:
            return False

        # Prepare points for upsert
        points = []
        for chunk in chunks:
            point = qdrant_models.PointStruct(
                id=str(hash(chunk.text)),  # Simple hash-based ID
                vector=chunk.embedding or [0.0] * 768,  # Default embedding if none provided
                payload={
                    "text": chunk.text,
                    "metadata": chunk.metadata
                }
            )
            points.append(point)

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return True
        except Exception as e:
            print(f"Error upserting chunks: {e}")
            return False

    def search_similar(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            return [{
                "text": result.payload["text"],
                "metadata": result.payload["metadata"],
                "score": result.score
            } for result in results]
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        try:
            return self.client.get_collection(self.collection_name).dict()
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {}


