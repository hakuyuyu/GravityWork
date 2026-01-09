import os
import tempfile
from typing import List, Dict, Optional
from dataclasses import dataclass
import PyPDF2
import docx
import logging

logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a chunk of document text with metadata"""
    text: str
    page_number: int
    chunk_index: int
    metadata: Dict[str, str]

class DocumentProcessor:
    """Handles document ingestion and processing"""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def process_document(self, file_path: str) -> List[DocumentChunk]:
        """Process a document file and return chunks"""
        try:
            text = self._extract_text(file_path)
            chunks = self._chunk_text(text)
            return chunks
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise

    def _extract_text(self, file_path: str) -> str:
        """Extract text from various document formats"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            return self._extract_pdf_text(file_path)
        elif ext == '.docx':
            return self._extract_docx_text(file_path)
        elif ext == '.txt':
            return self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF files"""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT files"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _chunk_text(self, text: str) -> List[DocumentChunk]:
        """Split text into chunks with overlap"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_index = 0
        page_number = 1  # Default page number

        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space

            if current_length >= self.chunk_size:
                chunk_text = " ".join(current_chunk)
                chunks.append(DocumentChunk(
                    text=chunk_text,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    metadata={"source": "document"}
                ))
                chunk_index += 1

                # Overlap: keep last few words for next chunk
                overlap_words = current_chunk[-self.overlap:] if self.overlap > 0 else []
                current_chunk = overlap_words
                current_length = sum(len(word) + 1 for word in overlap_words)

        # Add remaining words as last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(DocumentChunk(
                text=chunk_text,
                page_number=page_number,
                chunk_index=chunk_index,
                metadata={"source": "document"}
            ))

        return chunks

class DocumentPipeline:
    """Main document processing pipeline"""

    def __init__(self, processor: Optional[DocumentProcessor] = None):
        self.processor = processor or DocumentProcessor()

    def process_file(self, file_path: str) -> Dict:
        """Process a single document file"""
        try:
            chunks = self.processor.process_document(file_path)
            return {
                "status": "success",
                "file_path": file_path,
                "chunk_count": len(chunks),
                "chunks": [{"text": c.text, "metadata": c.metadata} for c in chunks]
            }
        except Exception as e:
            return {
                "status": "error",
                "file_path": file_path,
                "error": str(e)
            }

    def process_directory(self, directory_path: str) -> List[Dict]:
        """Process all documents in a directory"""
        results = []
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                result = self.process_file(file_path)
                results.append(result)
        return results
