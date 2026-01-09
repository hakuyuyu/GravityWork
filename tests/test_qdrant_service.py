"""
Tests for Qdrant Service
"""

import pytest
from backend.services.qdrant_service import QdrantService
from backend.services.chunking_service import ChunkingService

@pytest.fixture
def qdrant_service():
    """Fixture for Qdrant service (uses in-memory for testing)"""
    # For testing, we'll use a mock or local instance
    return QdrantService(host="localhost", port=6333)

@pytest.fixture
def chunking_service():
    """Fixture for chunking service"""
    return ChunkingService(chunk_size=100, overlap=20)

def test_chunking_service(chunking_service):
    """Test document chunking"""
    document = "This is a test document. " * 50
    metadata = {
        "project_id": "proj_001",
        "author": "test@example.com",
        "doc_type": "PRD"
    }

    chunks = chunking_service.chunk_document(document, metadata)

    assert len(chunks) > 1, "Document should be split into multiple chunks"
    assert all("doc_id" in chunk["metadata"] for chunk in chunks), "All chunks should have doc_id"
    assert all(chunk["metadata"]["doc_id"] == chunks[0]["metadata"]["doc_id"] for chunk in chunks), "All chunks should have same doc_id"

    # Test reconstruction
    reconstructed = chunking_service.reconstruct_document(chunks)
    assert "text" in reconstructed, "Reconstructed document should have text"
    assert "metadata" in reconstructed, "Reconstructed document should have metadata"

def test_qdrant_collection_operations(qdrant_service):
    """Test Qdrant collection operations"""
    collection_name = "test_collection"

    # Clean up if exists
    if qdrant_service.collection_exists(collection_name):
        qdrant_service.delete_collection(collection_name)

    # Test creation
    created = qdrant_service.create_collection(collection_name, vector_size=1536)
    assert created, "Collection should be created"

    # Test exists
    assert qdrant_service.collection_exists(collection_name), "Collection should exist"

    # Test info
    info = qdrant_service.get_collection_info(collection_name)
    assert info["name"] == collection_name, "Collection info should match"

    # Clean up
    qdrant_service.delete_collection(collection_name)
    assert not qdrant_service.collection_exists(collection_name), "Collection should be deleted"

def test_qdrant_vector_operations(qdrant_service):
    """Test Qdrant vector operations"""
    collection_name = "test_vectors"

    # Create collection
    qdrant_service.create_collection(collection_name, vector_size=4)

    # Prepare test vectors
    test_vectors = [
        {
            "id": 1,
            "vector": [0.1, 0.2, 0.3, 0.4],
            "metadata": {"doc_type": "PRD", "project": "test"}
        },
        {
            "id": 2,
            "vector": [0.5, 0.6, 0.7, 0.8],
            "metadata": {"doc_type": "PRD", "project": "test"}
        }
    ]

    # Test upsert
    upserted = qdrant_service.upsert_vectors(collection_name, test_vectors)
    assert upserted, "Vectors should be upserted"

    # Test search
    query_vector = [0.1, 0.2, 0.3, 0.4]
    results = qdrant_service.search_vectors(collection_name, query_vector, limit=2)
    assert len(results) > 0, "Search should return results"
    assert results[0]["score"] >= 0, "Score should be non-negative"

    # Clean up
    qdrant_service.delete_collection(collection_name)
