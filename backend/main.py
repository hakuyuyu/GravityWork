from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services.qdrant_service import QdrantService
from backend.services.chunking_service import HierarchicalChunkingService as DocumentChunker
from backend.routers import chat
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
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
qdrant_service = QdrantService()
document_chunker = DocumentChunker()

# Include Routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

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
        chunks = document_chunker.create_hierarchical_chunks(
            document["text"],
            document.get("metadata", {})
        )

        # Prepare vectors for Qdrant (using dummy vectors for now)
        # Note: In real app, we'd generate embeddings here
        # For now, relying on service to handle or use placeholder
        success = qdrant_service.upsert_chunks(chunks)
        
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
        results = qdrant_service.search_similar(
            query_text=query,
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
