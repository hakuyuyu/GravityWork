"""
Qdrant Vector Database Service for GravityWork.
Handles document embeddings and semantic search.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

import structlog
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

logger = structlog.get_logger()


class DocumentChunk(BaseModel):
    """A document chunk with metadata."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class SearchResult(BaseModel):
    """Search result from Qdrant."""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]


class QdrantService:
    """
    Service for interacting with Qdrant vector database.
    
    Implements hierarchical chunking strategy for document retrieval.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "gravitywork_docs"
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self._client: Optional[QdrantClient] = None
    
    @property
    def client(self) -> QdrantClient:
        """Lazy initialization of Qdrant client."""
        if self._client is None:
            self._client = QdrantClient(host=self.host, port=self.port)
            logger.info("qdrant_connected", host=self.host, port=self.port)
        return self._client
    
    async def ensure_collection(self, vector_size: int = 1536):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=vector_size,
                    distance=qdrant_models.Distance.COSINE
                )
            )
            logger.info("qdrant_collection_created", name=self.collection_name)
        
        return exists
    
    async def upsert_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Insert or update document chunks."""
        points = [
            qdrant_models.PointStruct(
                id=chunk.id,
                vector=chunk.embedding,
                payload={
                    "content": chunk.content,
                    **chunk.metadata,
                    "indexed_at": datetime.utcnow().isoformat()
                }
            )
            for chunk in chunks
            if chunk.embedding is not None
        ]
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info("qdrant_upserted", count=len(points))
        
        return len(points)
    
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Semantic search for relevant documents."""
        
        # Build filter if provided
        qdrant_filter = None
        if filters:
            conditions = [
                qdrant_models.FieldCondition(
                    key=key,
                    match=qdrant_models.MatchValue(value=value)
                )
                for key, value in filters.items()
            ]
            qdrant_filter = qdrant_models.Filter(must=conditions)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=qdrant_filter
        )
        
        return [
            SearchResult(
                id=str(hit.id),
                content=hit.payload.get("content", ""),
                score=hit.score,
                metadata={
                    k: v for k, v in hit.payload.items() 
                    if k != "content"
                }
            )
            for hit in results
        ]
    
    async def delete_by_project(self, project_id: str) -> int:
        """Delete all chunks for a project."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=qdrant_models.FilterSelector(
                filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="project_id",
                            match=qdrant_models.MatchValue(value=project_id)
                        )
                    ]
                )
            )
        )
        logger.info("qdrant_deleted_project", project_id=project_id)
        return 1  # Qdrant doesn't return count
    
    async def health_check(self) -> bool:
        """Check if Qdrant is reachable."""
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error("qdrant_health_failed", error=str(e))
            return False
