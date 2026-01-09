from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.app.services.qdrant_service import QdrantService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    project_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    context: Optional[list] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint for handling chat messages.

    Args:
        request: ChatRequest containing the user's message and optional project_id.

    Returns:
        ChatResponse containing the AI's response and optional context.
    """
    try:
        # Initialize Qdrant service
        qdrant_service = QdrantService()

        # Retrieve context from Qdrant (if project_id is provided)
        context = None
        if request.project_id:
            context = qdrant_service.search(request.project_id, request.message)

        # Simulate AI response (replace with actual AI model call)
        response = f"AI Response: {request.message}"

        return ChatResponse(response=response, context=context)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
