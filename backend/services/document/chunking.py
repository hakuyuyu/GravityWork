import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

class DocumentChunker:
    """
    Hierarchical document chunking service.
    Splits documents into chunks suitable for vector embedding.
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize the document chunker.

        Args:
            chunk_size: Target size for each chunk (in characters)
            overlap: Overlap between chunks to maintain context
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        if not text:
            return []

        # Clean text
        text = self._clean_text(text)

        # Split into sentences first (if possible)
        sentences = self._split_into_sentences(text)
        if not sentences:
            return [text]

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence would exceed chunk size (accounting for overlap)
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Keep overlap by carrying forward some sentences
                overlap_sentences = current_chunk[-self.overlap:] if self.overlap > 0 else []
                current_chunk = overlap_sentences
                current_length = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add the last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple heuristics."""
        # Split on common sentence terminators followed by whitespace or capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

        # If no sentences found, try simpler splitting
        if len(sentences) == 1:
            sentences = re.split(r'(?<=[.!?])\s+', text)

        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def chunk_with_metadata(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Chunk text and attach metadata to each chunk.

        Args:
            text: Input text
            metadata: Metadata to attach to chunks

        Returns:
            List of chunks with metadata
        """
        chunks = self.chunk_text(text)
        return [
            {
                "text": chunk,
                "metadata": metadata,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            for i, chunk in enumerate(chunks)
        ]
