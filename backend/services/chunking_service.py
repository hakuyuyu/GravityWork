"""
Hierarchical Chunking Service for GravityWork

This service implements hierarchical chunking for documents to preserve context
while enabling efficient vector search.
"""

from typing import List, Dict, Any
import hashlib
import json

class ChunkingService:
    """
    Service for hierarchical document chunking.
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 100):
        """
        Initialize chunking service.

        Args:
            chunk_size: Target size for chunks (in characters)
            overlap: Overlap between chunks to preserve context
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(
        self,
        document: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunk a document hierarchically.

        Args:
            document: The document text to chunk
            metadata: Metadata to attach to all chunks

        Returns:
            List of chunks with metadata
        """
        # Generate document ID
        doc_id = self._generate_doc_id(document, metadata)

        # Split into chunks
        chunks = self._split_text(document, self.chunk_size, self.overlap)

        # Create chunk objects
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "doc_id": doc_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk)
            }

            chunk_objects.append({
                "id": f"{doc_id}_chunk_{i}",
                "text": chunk,
                "metadata": chunk_metadata
            })

        return chunk_objects

    def _split_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Split text into chunks with overlap.

        Args:
            text: Text to split
            chunk_size: Target chunk size
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunks.append(text[start:end])

            # Move start forward by chunk_size - overlap
            start = start + chunk_size - overlap

        return chunks

    def _generate_doc_id(self, document: str, metadata: Dict[str, Any]) -> str:
        """
        Generate a unique document ID based on content and metadata.

        Args:
            document: Document content
            metadata: Document metadata

        Returns:
            Unique document ID
        """
        # Create a hash of document content and key metadata
        hash_input = f"{document[:100]}{json.dumps(metadata, sort_keys=True)}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def reconstruct_document(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Reconstruct a document from its chunks.

        Args:
            chunks: List of chunk objects

        Returns:
            Reconstructed document with metadata
        """
        if not chunks:
            return {"text": "", "metadata": {}}

        # Get metadata from first chunk
        metadata = chunks[0]["metadata"].copy()

        # Remove chunk-specific metadata
        metadata.pop("chunk_index", None)
        metadata.pop("total_chunks", None)
        metadata.pop("chunk_size", None)

        # Reconstruct text (simple concatenation with overlap handling)
        text_parts = []
        for chunk in chunks:
            text_parts.append(chunk["text"])

        # Join with spaces to handle overlaps
        reconstructed_text = " ".join(text_parts)

        return {
            "text": reconstructed_text,
            "metadata": metadata
        }
