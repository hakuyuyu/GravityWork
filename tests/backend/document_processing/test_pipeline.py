import unittest
import tempfile
import os
from backend.src.document_processing.pipeline import DocumentProcessor, DocumentPipeline, DocumentChunk

class TestDocumentProcessing(unittest.TestCase):
    """Tests for Document Processing Pipeline"""

    def setUp(self):
        self.processor = DocumentProcessor(chunk_size=50, overlap=10)
        self.pipeline = DocumentPipeline(self.processor)

    def test_pdf_extraction(self):
        """Test PDF text extraction"""
        pdf_content = "Sample PDF content for testing"
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            # Create a simple PDF
            from PyPDF2 import PdfWriter
            writer = PdfWriter()
            writer.add_blank_page(width=72, height=72)
            writer.write(f)
            temp_file = f.name

        try:
            text = self.processor._extract_pdf_text(temp_file)
            self.assertIsInstance(text, str)
        finally:
            os.unlink(temp_file)

    def test_txt_extraction(self):
        """Test TXT text extraction"""
        sample_text = "This is a test document\nwith multiple lines."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_text)
            temp_file = f.name

        try:
            text = self.processor._extract_txt_text(temp_file)
            self.assertEqual(text, sample_text)
        finally:
            os.unlink(temp_file)

    def test_chunking(self):
        """Test text chunking"""
        long_text = " ".join([f"word{i}" for i in range(100)])
        chunks = self.processor._chunk_text(long_text)

        self.assertGreater(len(chunks), 1)
        self.assertIsInstance(chunks[0], DocumentChunk)
        self.assertLessEqual(len(chunks[0].text), self.processor.chunk_size + 10)

    def test_pipeline_processing(self):
        """Test full pipeline processing"""
        sample_text = "Sample document content for pipeline testing."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_text)
            temp_file = f.name

        try:
            result = self.pipeline.process_file(temp_file)
            self.assertEqual(result['status'], 'success')
            self.assertGreater(result['chunk_count'], 0)
        finally:
            os.unlink(temp_file)

    def test_unsupported_format(self):
        """Test handling of unsupported file formats"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("content")
            temp_file = f.name

        try:
            with self.assertRaises(ValueError):
                self.processor.process_document(temp_file)
        finally:
            os.unlink(temp_file)

if __name__ == "__main__":
    unittest.main()
