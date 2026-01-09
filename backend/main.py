from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services.qdrant.qdrant_service import QdrantService
from backend.services.chunking_service import HierarchicalChunkingService as DocumentChunker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GravityWork Backend",
    description="Backend API for GravityWork",
    version="0.1.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
qdrant_service = QdrantService()
document_chunker = DocumentChunker()

@app.get("/")
async def root():
    return {"message": "GravityWork API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/collections/{collection_name}")
async def create_collection(collection_name: str):
    """
    Create a new Qdrant collection.

    Args:
        collection_name: Name of the collection to create

    Returns:
        Success status
    """
    try:
        success = qdrant_service.create_collection(collection_name)
        if success:
            return {"status": "success", "collection": collection_name}
        else:
            raise HTTPException(status_code=500, detail="Failed to create collection")
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_name}")
async def get_collection(collection_name: str):
    """
    Get information about a collection.

    Args:
        collection_name: Name of the collection

    Returns:
        Collection information
    """
    try:
        info = qdrant_service.get_collection_info(collection_name)
        if info:
            return info
        else:
            raise HTTPException(status_code=404, detail="Collection not found")
    except Exception as e:
        logger.error(f"Error getting collection info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collections/{collection_name}/documents")
async def upsert_document(collection_name: str, document: dict):
    """
    Upsert a document into a collection.

    Args:
        collection_name: Target collection
        document: Document data with 'text' and optional 'metadata'

    Returns:
        Success status
    """
    try:
        # Validate input
        if "text" not in document:
            raise HTTPException(status_code=400, detail="Document text is required")

        # Chunk the document
        chunks = document_chunker.chunk_with_metadata(
            document["text"],
            document.get("metadata", {})
        )

        # Prepare vectors for Qdrant (using dummy vectors for now)
        vectors = []
        for i, chunk in enumerate(chunks):
            vectors.append({
                "id": f"{document.get('id', 'doc')}_{i}",
                "vector": [0.0] * 1536,  # Placeholder - would be real embeddings
                "payload": {
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                    "chunk_index": chunk["chunk_index"],
                    "total_chunks": chunk["total_chunks"]
                }
            })

        # Upsert vectors
        success = qdrant_service.upsert_vectors(collection_name, vectors)
        if success:
            return {
                "status": "success",
                "chunks_created": len(chunks),
                "collection": collection_name
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to upsert document")
    except Exception as e:
        logger.error(f"Error upserting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_name}/search")
async def search_collection(collection_name: str, query: str, limit: int = 5):
    """
    Search a collection.

    Args:
        collection_name: Collection to search
        query: Search query text
        limit: Maximum results to return

    Returns:
        Search results
    """
    try:
        # In a real implementation, we would embed the query here
        # For now, using a dummy vector
        query_vector = [0.1] * 1536

        results = qdrant_service.search_vectors(
            collection_name,
            query_vector,
            limit=limit
        )

        return {
            "results": results,
            "query": query,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error searching collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
