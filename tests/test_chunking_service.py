import pytest
from backend.services.chunking_service import HierarchicalChunkingService, Chunk

@pytest.fixture
def chunking_service():
    """Fixture for chunking service."""
    return HierarchicalChunkingService(max_chunk_size=100, overlap=20)

def test_chunk_text_empty(chunking_service):
    """Test chunking empty text."""
    chunks = chunking_service.chunk_text("", "doc_1")
    assert len(chunks) == 0

def test_chunk_text_single_paragraph(chunking_service):
    """Test chunking single paragraph."""
    text = "This is a short paragraph that should fit in one chunk."
    chunks = chunking_service.chunk_text(text, "doc_1")

    assert len(chunks) == 1
    assert chunks[0].content == text
    assert chunks[0].metadata["document_id"] == "doc_1"

def test_chunk_text_multiple_paragraphs(chunking_service):
    """Test chunking multiple paragraphs."""
    text = """This is the first paragraph.

This is the second paragraph.

This is the third paragraph."""
    chunks = chunking_service.chunk_text(text, "doc_1")

    # Should create multiple chunks
    assert len(chunks) > 1
    assert all(chunk.metadata["document_id"] == "doc_1" for chunk in chunks)

def test_chunk_with_hierarchy(chunking_service):
    """Test hierarchical chunking."""
    text = """First paragraph.

Second paragraph.

Third paragraph."""
    chunks = chunking_service.chunk_with_hierarchy(text, "doc_1")

    assert len(chunks) > 1
    assert chunks[0]["metadata"]["is_first"] is True
    assert chunks[-1]["metadata"]["is_last"] is True
    assert chunks[0]["metadata"]["total_chunks"] == len(chunks)

def test_chunk_overlap(chunking_service):
    """Test chunk overlap."""
    # Create text that will require multiple chunks
    text = "A" * 150  # Longer than max_chunk_size
    chunks = chunking_service.chunk_text(text, "doc_1")

    assert len(chunks) > 1

    # Check that chunks overlap
    first_chunk = chunks[0].content
    second_chunk = chunks[1].content

    # The beginning of second chunk should overlap with end of first
    overlap_region = first_chunk[-20:]  # overlap size
    assert second_chunk.startswith(overlap_region)
