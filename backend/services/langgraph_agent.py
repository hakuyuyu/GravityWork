from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import os
import operator
import logging

logger = logging.getLogger(__name__)

# Define Agent State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    scratchpad: dict

class LangGraphAgent:
    """
    Orchestrates complex tasks using LangGraph.
    Uses lazy initialization for the LLM to avoid crashes when API key is not set.
    """
    def __init__(self):
        self._llm = None
        self._workflow = None
    
    @property
    def llm(self):
        """Lazy initialization of LLM."""
        if self._llm is None:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                try:
                    from langchain_openai import ChatOpenAI
                    self._llm = ChatOpenAI(
                        model=os.getenv("MODEL", "gpt-3.5-turbo"),
                        api_key=api_key,
                        base_url="https://openrouter.ai/api/v1"
                    )
                    logger.info("LLM initialized with OpenRouter")
                except Exception as e:
                    logger.warning(f"Failed to initialize LLM: {e}")
                    self._llm = None
            else:
                logger.warning("No OPENROUTER_API_KEY set, running in mock mode")
        return self._llm
    
    @property
    def workflow(self):
        """Lazy initialization of workflow."""
        if self._workflow is None:
            self._workflow = self._build_graph()
        return self._workflow

    def _build_graph(self):
        """Builds the LangGraph workflow."""
        workflow = StateGraph(AgentState)

        # Define Nodes
        workflow.add_node("scout", self._scout_node)
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("execute", self._execute_node)

        # Define Edges
        workflow.set_entry_point("scout")
        workflow.add_edge("scout", "plan")
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", END)

        return workflow.compile()

    async def _scout_node(self, state: AgentState):
        """Gather context (Jira, Docs) before planning."""
        user_query = state["messages"][0].content if state["messages"] else ""
        
        # In a real implementation, we would:
        # 1. Query Qdrant for relevant documents
        # 2. Query Jira MCP for related tickets
        context = f"Scouting context for: '{user_query}'"
        return {"messages": [AIMessage(content=context)], "scratchpad": {"query": user_query}}

    async def _plan_node(self, state: AgentState):
        """Decide on the action plan."""
        query = state.get("scratchpad", {}).get("query", "")
        
        # Simple rule-based planning
        if "create" in query.lower():
            plan = "Action Plan: Create a new ticket/item"
        elif "update" in query.lower() or "change" in query.lower():
            plan = "Action Plan: Update existing resource"
        elif "status" in query.lower():
            plan = "Action Plan: Retrieve status from Jira"
        else:
            plan = "Action Plan: Provide information from knowledge base"
        
        return {"messages": [AIMessage(content=plan)]}

    async def _execute_node(self, state: AgentState):
        """Execute the planned tools."""
        plan = state["messages"][-1].content if state["messages"] else ""
        
        # Mock execution - in real implementation, this calls MCP tools
        if "Create" in plan:
            result = "✅ [Mock] Ticket created successfully. ID: MOCK-123"
        elif "Update" in plan:
            result = "✅ [Mock] Resource updated successfully."
        elif "status" in plan.lower() or "Retrieve" in plan:
            result = "📋 [Mock] Status: In Progress. Assigned to: developer@example.com"
        else:
            result = "ℹ️ [Mock] Information retrieved from knowledge base."
        
        return {"messages": [AIMessage(content=result)]}

    async def run(self, query: str) -> str:
        """Run the agent workflow."""
        try:
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "next_step": "scout",
                "scratchpad": {}
            }
            
            results = await self.workflow.ainvoke(initial_state)
            return results["messages"][-1].content
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return f"Agent execution failed: {str(e)}"
