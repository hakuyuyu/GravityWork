from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.services.intent_router import IntentRouter, IntentType
from backend.services.langgraph_agent import LangGraphAgent
from backend.services.qdrant_service import QdrantService
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Services
# We initialize logically, but in a real app might use dependency injection
intent_router = IntentRouter()
agent = LangGraphAgent()
qdrant_service = QdrantService()

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    sources: Optional[List[Dict[str, Any]]] = None
    conversation_id: Optional[str] = None
    timestamp: str

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that routes through the Logic Layer.
    """
    try:
        # 1. Classify Intent
        classification = await intent_router.classify(request.message)
        logger.info(f"Intent classified: {classification}")

        response_text = ""
        sources = []

        # 2. Route based on Intent
        if classification.intent == IntentType.ACTION:
            # Delegate to Agent
            response_text = await agent.run(request.message)
            
        elif classification.intent == IntentType.TRIAGE:
            # Simple Triage (Sprint 2 Placeholder)
            response_text = f"I see you want to check status ({classification.reasoning}). I'll check Jira..."
            response_text += "\n\n(Note: Triage Agent logic pending full Jira connection in Sprint 3)"

        else: # DIRECT_ANSWER / UNKNOWN
            # Retrieval (RAG)
            # Embed query (mock) and search Qdrant
            # In a real app we'd embed the query
            query_vector = [0.1] * 768 # Dummy vector
            results = qdrant_service.search_similar(query_vector, limit=3)
            
            # Simple generation (Mock LLM response for Direct Answer if no LLM connected for RAG)
            if results:
                context = "\n".join([f"- {r['text']}" for r in results])
                response_text = f"Based on knowledge base:\n{context[:500]}..."
                sources = results
            else:
                response_text = "I couldn't find any specific documents about that in the knowledge base."

        return ChatResponse(
            response=response_text,
            intent=classification.intent,
            confidence=classification.confidence,
            sources=sources,
            conversation_id=request.conversation_id,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
