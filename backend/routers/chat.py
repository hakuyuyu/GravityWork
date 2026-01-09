from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Lazy service initialization to avoid import-time failures
_intent_router = None
_agent = None
_qdrant_service = None

def get_intent_router():
    global _intent_router
    if _intent_router is None:
        from backend.services.intent_router import IntentRouter
        _intent_router = IntentRouter()
    return _intent_router

def get_agent():
    global _agent
    if _agent is None:
        from backend.services.langgraph_agent import LangGraphAgent
        _agent = LangGraphAgent()
    return _agent

def get_qdrant_service():
    global _qdrant_service
    if _qdrant_service is None:
        from backend.services.qdrant_service import QdrantService
        _qdrant_service = QdrantService()
    return _qdrant_service

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
    from backend.services.intent_router import IntentType
    
    try:
        intent_router = get_intent_router()
        agent = get_agent()
        qdrant_service = get_qdrant_service()
        
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
            # Delegate to Agent for triage as well
            response_text = await agent.run(request.message)

        else: # DIRECT_ANSWER / UNKNOWN
            # Retrieval (RAG)
            try:
                query_vector = [0.1] * 768  # Dummy vector
                results = qdrant_service.search_similar(query_vector, limit=3)
                
                if results:
                    context = "\n".join([f"- {r['text']}" for r in results])
                    response_text = f"Based on knowledge base:\n{context[:500]}..."
                    sources = results
                else:
                    response_text = "I couldn't find any specific documents about that in the knowledge base."
            except Exception as e:
                logger.warning(f"Qdrant search failed: {e}")
                response_text = "Knowledge base is not available. Please check Qdrant connection."

        return ChatResponse(
            response=response_text,
            intent=classification.intent.value,
            confidence=classification.confidence,
            sources=sources,
            conversation_id=request.conversation_id,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
