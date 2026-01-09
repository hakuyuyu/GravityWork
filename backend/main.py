from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services.qdrant_service import QdrantService

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Qdrant service
qdrant_service = QdrantService()

@app.on_event("startup")
async def startup_event():
    """Initialize Qdrant collection on startup"""
    if not qdrant_service.collection_exists():
        qdrant_service.create_collection()
        print("Qdrant collection created")
    else:
        print("Qdrant collection already exists")

@app.get("/")
async def root():
    return {"message": "GravityWork API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/qdrant/info")
async def qdrant_info():
    """Get Qdrant collection information"""
    return qdrant_service.get_collection_info()
