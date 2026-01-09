from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel
import re

class IntentType(str, Enum):
    DIRECT_ANSWER = "direct_answer"  # RAG/Knowledge base
    TRIAGE = "triage"                # Jira/GitHub lookup
    ACTION = "action"                # Create/Update tickets
    UNKNOWN = "unknown"

class IntentClassification(BaseModel):
    intent: IntentType
    confidence: float
    reasoning: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class IntentRouter:
    """
    Classifies user queries to determine the appropriate handling strategy.
    """
    
    def __init__(self):
        # Keyword mappings for heuristic classification
        self.triage_keywords = [
            r"jira", r"ticket", r"issue", r"bug", r"feature", r"sprint", 
            r"backlog", r"board", r"github", r"pr", r"pull request", r"commit", 
            r"status of", r"who is working on", r"what is the status"
        ]
        self.action_keywords = [
            r"create", r"update", r"delete", r"assign", r"close", r"open", 
            r"move", r"change", r"start", r"deploy", r"run"
        ]
    
    async def classify(self, query: str) -> IntentClassification:
        """
        Classifies the intent of a user query.
        """
        query_lower = query.lower()
        
        # 1. Heuristic Check (Fast Path)
        
        # Check for Action keywords
        for pattern in self.action_keywords:
            if re.search(pattern, query_lower):
                return IntentClassification(
                    intent=IntentType.ACTION,
                    confidence=0.7,
                    reasoning=f"Detected action keyword: {pattern}"
                )
        
        # Check for Triage keywords
        for pattern in self.triage_keywords:
            if re.search(pattern, query_lower):
                return IntentClassification(
                    intent=IntentType.TRIAGE,
                    confidence=0.8,
                    reasoning=f"Detected triage keyword: {pattern}"
                )
        
        # Default to Direct Answer (RAG) if no specific keywords found
        # In a full implementation, we would call an LLM here for ambiguity
        return IntentClassification(
            intent=IntentType.DIRECT_ANSWER,
            confidence=0.5,
            reasoning="No specific keywords found, defaulting to knowledge retrieval"
        )
