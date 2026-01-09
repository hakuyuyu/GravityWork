import pytest
from backend.services.qdrant_service import QdrantService, DocumentChunk, HierarchicalChunkingService

def test_hierarchical_chunking():
    """Test hierarchical document chunking"""
    document = "This is a test document. " * 100
    metadata = {
        "project_id": "proj_001",
        "author": "test@example.com",
        "doc_type": "test"
    }

    chunks = HierarchicalChunkingService.create_hierarchical_chunks(document, metadata)

    # Should have 1 parent + multiple children
    assert len(chunks) > 1
    assert chunks[0].metadata["chunk_type"] == "parent"
    assert chunks[0].metadata["chunk_level"] == 0

    # Check child chunks
    for chunk in chunks[1:]:
        assert chunk.metadata["chunk_type"] == "child"
        assert chunk.metadata["chunk_level"] == 1
        assert "chunk_index" in chunk.metadata

def test_qdrant_service_initialization():
    """Test Qdrant service initialization"""
    service = QdrantService()
    assert service.client is not None
    assert service.collection_name == "documents"

def test_qdrant_collection_operations():
    """Test Qdrant collection operations"""
    service = QdrantService()

    # Create collection
    if service.collection_exists():
        # Collection already exists (from previous test runs)
        info = service.get_collection_info()
        assert "vectors" in info
    else:
        result = service.create_collection()
        assert result is True
        assert service.collection_exists() is True

    # Test upsert and search
    chunk = DocumentChunk(
        text="Test document chunk",
        metadata={"test": "data"},
        embedding=[0.1] * 768
    )

    result = service.upsert_chunks([chunk])
    assert result is True

    # Search
    query_vector = [0.1] * 768
    results = service.search_similar(query_vector, limit=1)
    assert len(results) > 0
    assert results[0]["text"] == "Test document chunk"
