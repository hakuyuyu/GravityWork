from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ChunkingService:
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Chunk text into smaller segments with metadata."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append({
                "text": chunk,
                "metadata": metadata,
                "chunk_id": f"{metadata.get('doc_id', 'unknown')}_{i}"
            })
        logger.info(f"Chunked text into {len(chunks)} chunks.")
        return chunks

    def hierarchical_chunk(self, document: Dict) -> List[Dict]:
        """Hierarchical chunking for documents."""
        parent_metadata = {
            "doc_id": document["id"],
            "doc_type": document["type"],
            "author": document.get("author", "unknown"),
            "timestamp": document.get("timestamp", "unknown")
        }
        return self.chunk_text(document["content"], parent_metadata)
