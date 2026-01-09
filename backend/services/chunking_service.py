from typing import List, Dict, Any, Optional
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class Chunk(BaseModel):
    """Represents a chunk of a document with metadata"""
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class HierarchicalChunkingService:
    """Service for hierarchical document chunking"""
    
    def __init__(self, max_chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_document(self, document: str) -> List[str]:
        """Split document into chunks with overlap"""
        chunks = []
        start = 0
        while start < len(document):
            end = min(start + self.chunk_size, len(document))
            chunks.append(document[start:end])
            if end == len(document):
                break
            start = end - self.overlap
        return chunks

    def create_hierarchical_chunks(self, document: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Create hierarchical chunks with metadata"""
        # Parent document chunk
        parent_chunk = Chunk(
            text=document,
            metadata={
                **metadata,
                "chunk_type": "parent",
                "chunk_level": 0
            }
        )

        # Child chunks
        text_chunks = self.chunk_document(document)
        child_chunks = []
        for i, chunk in enumerate(text_chunks):
            child_chunks.append(Chunk(
                text=chunk,
                metadata={
                    **metadata,
                    "chunk_type": "child",
                    "chunk_level": 1,
                    "chunk_index": i,
                    "parent_id": str(hash(document))
                }
            ))

        return [parent_chunk] + child_chunks
