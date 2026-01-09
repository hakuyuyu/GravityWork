from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory store for pending actions (would use Redis in production)
_pending_actions: Dict[str, Dict[str, Any]] = {}

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

class PendingAction(BaseModel):
    action_id: str
    action_type: str
    description: str
    parameters: Dict[str, Any]

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    sources: Optional[List[Dict[str, Any]]] = None
    conversation_id: Optional[str] = None
    timestamp: str
    requires_confirmation: bool = False
    pending_action: Optional[PendingAction] = None

class ConfirmRequest(BaseModel):
    action_id: str
    approved: bool

class ConfirmResponse(BaseModel):
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None

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
        requires_confirmation = False
        pending_action = None

        # 2. Route based on Intent
        if classification.intent == IntentType.ACTION:
            # For destructive actions, require confirmation
            message_lower = request.message.lower()
            
            if any(word in message_lower for word in ["create", "delete", "update", "change"]):
                # Create pending action for approval
                action_id = str(uuid.uuid4())[:8]
                action_data = {
                    "type": "create_ticket" if "create" in message_lower else "update",
                    "query": request.message,
                    "created_at": datetime.utcnow().isoformat()
                }
                _pending_actions[action_id] = action_data
                
                requires_confirmation = True
                pending_action = PendingAction(
                    action_id=action_id,
                    action_type=action_data["type"],
                    description=f"Execute: {request.message}",
                    parameters={"query": request.message}
                )
                response_text = f"⚠️ **Confirmation Required**\n\nI'm about to perform the following action:\n" \
                               f"**{action_data['type'].title()}**: {request.message}\n\n" \
                               f"Please confirm by calling `/api/chat/confirm` with action_id: `{action_id}`"
            else:
                # Non-destructive action, execute directly
                response_text = await agent.run(request.message)
            
        elif classification.intent == IntentType.TRIAGE:
            # Triage is read-only, no confirmation needed
            response_text = await agent.run(request.message)

        else: # DIRECT_ANSWER / UNKNOWN
            # Delegate to Agent (which now has Qdrant scouting)
            response_text = await agent.run(request.message)

        return ChatResponse(
            response=response_text,
            intent=classification.intent.value,
            confidence=classification.confidence,
            sources=sources,
            conversation_id=request.conversation_id,
            timestamp=datetime.utcnow().isoformat(),
            requires_confirmation=requires_confirmation,
            pending_action=pending_action
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm", response_model=ConfirmResponse)
async def confirm_action(request: ConfirmRequest):
    """
    Confirm or reject a pending action (Human-in-the-Loop).
    """
    action_id = request.action_id
    
    if action_id not in _pending_actions:
        raise HTTPException(status_code=404, detail=f"Action {action_id} not found or expired")
    
    action = _pending_actions.pop(action_id)
    
    if request.approved:
        # Execute the pending action
        agent = get_agent()
        try:
            result = await agent.run(action["query"])
            return ConfirmResponse(
                status="executed",
                message=f"Action completed successfully",
                result={"response": result}
            )
        except Exception as e:
            return ConfirmResponse(
                status="failed",
                message=f"Action failed: {str(e)}"
            )
    else:
        return ConfirmResponse(
            status="cancelled",
            message="Action was cancelled by user"
        )

@router.get("/pending")
async def get_pending_actions():
    """List all pending actions awaiting confirmation."""
    return {
        "pending_count": len(_pending_actions),
        "actions": [
            {"action_id": k, **v}
            for k, v in _pending_actions.items()
        ]
    }
