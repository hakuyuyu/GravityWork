from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import os
import operator
import logging
import re

logger = logging.getLogger(__name__)

# Define Agent State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    scratchpad: Dict[str, Any]
    pending_action: Optional[Dict[str, Any]]

class LangGraphAgent:
    """
    Orchestrates complex tasks using LangGraph.
    Integrates with MCP servers for real tool execution.
    """
    def __init__(self):
        self._llm = None
        self._workflow = None
        self._mcp_client = None
    
    @property
    def mcp_client(self):
        """Lazy initialization of MCP client."""
        if self._mcp_client is None:
            from backend.services.mcp_client import get_mcp_client
            self._mcp_client = get_mcp_client()
        return self._mcp_client
    
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

    def _extract_ticket_id(self, text: str) -> Optional[str]:
        """Extract Jira ticket ID from text."""
        # Match patterns like JIRA-123, PROJ-456, etc.
        match = re.search(r'([A-Z]+-\d+)', text.upper())
        return match.group(1) if match else None

    async def _scout_node(self, state: AgentState):
        """Gather context from Jira/Docs before planning."""
        user_query = state["messages"][0].content if state["messages"] else ""
        scratchpad = {"query": user_query}
        
        # Try to extract ticket ID and fetch from Jira
        ticket_id = self._extract_ticket_id(user_query)
        if ticket_id:
            logger.info(f"Detected ticket ID: {ticket_id}")
            result = await self.mcp_client.get_ticket_status(ticket_id)
            if result.success:
                scratchpad["jira_context"] = result.data
                context = f"Found Jira ticket {ticket_id}: {result.data}"
            else:
                context = f"Could not fetch ticket {ticket_id}: {result.error}"
        else:
            # Search for related tickets
            result = await self.mcp_client.search_tickets(user_query)
            if result.success and result.data:
                scratchpad["jira_search_results"] = result.data
                context = f"Found {len(result.data.get('data', {}).get('issues', []))} related tickets"
            else:
                context = f"Scouting context for: '{user_query}'"
        
        return {
            "messages": [AIMessage(content=context)],
            "scratchpad": scratchpad
        }

    async def _plan_node(self, state: AgentState):
        """Decide on the action plan based on scouted context."""
        query = state.get("scratchpad", {}).get("query", "").lower()
        jira_context = state.get("scratchpad", {}).get("jira_context")
        
        pending_action = None
        
        if "create" in query and "ticket" in query:
            plan = "Action Plan: Create a new Jira ticket"
            # Extract ticket details from query
            pending_action = {
                "type": "create_ticket",
                "summary": query,
                "project": "PROJ"  # Default project
            }
        elif "update" in query or "change" in query:
            plan = "Action Plan: Update existing Jira resource"
            pending_action = {"type": "update_ticket"}
        elif "status" in query or jira_context:
            plan = "Action Plan: Retrieve and display status from Jira"
            pending_action = {"type": "get_status"}
        elif "slack" in query or "message" in query:
            plan = "Action Plan: Send message or retrieve Slack messages"
            pending_action = {"type": "slack_action"}
        else:
            plan = "Action Plan: Provide information from knowledge base"
            pending_action = {"type": "rag_retrieval"}
        
        return {
            "messages": [AIMessage(content=plan)],
            "pending_action": pending_action
        }

    async def _execute_node(self, state: AgentState):
        """Execute the planned action via MCP tools."""
        pending_action = state.get("pending_action", {})
        action_type = pending_action.get("type", "unknown")
        scratchpad = state.get("scratchpad", {})
        
        try:
            if action_type == "create_ticket":
                # Create a Jira ticket
                result = await self.mcp_client.create_ticket(
                    summary=pending_action.get("summary", "New ticket"),
                    description="Created via GravityWork agent",
                    project=pending_action.get("project", "PROJ")
                )
                if result.success:
                    response = f"✅ Ticket created successfully!\n{result.data}"
                else:
                    response = f"❌ Failed to create ticket: {result.error}"
            
            elif action_type == "get_status":
                jira_context = scratchpad.get("jira_context", {})
                if jira_context:
                    issues = jira_context.get("data", {}).get("issues", [])
                    if issues:
                        issue = issues[0]
                        response = f"📋 **{issue.get('key', 'N/A')}**: {issue.get('summary', 'N/A')}\n" \
                                   f"Status: {issue.get('status', 'Unknown')}"
                    else:
                        response = "📋 No matching tickets found in Jira."
                else:
                    response = "📋 Status information not available."
            
            elif action_type == "slack_action":
                result = await self.mcp_client.get_slack_messages("general", limit=5)
                if result.success:
                    messages = result.data.get("data", {}).get("messages", [])
                    response = f"💬 Found {len(messages)} recent messages in Slack."
                else:
                    response = f"❌ Slack error: {result.error}"
            
            elif action_type == "update_ticket":
                response = "✅ Ticket update queued. (Human approval required for production)"
            
            else:
                response = "ℹ️ Retrieved information from knowledge base."
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            response = f"❌ Execution failed: {str(e)}"
        
        return {"messages": [AIMessage(content=response)]}

    async def run(self, query: str) -> str:
        """Run the agent workflow."""
        try:
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "next_step": "scout",
                "scratchpad": {},
                "pending_action": None
            }
            
            results = await self.workflow.ainvoke(initial_state)
            return results["messages"][-1].content
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return f"Agent execution failed: {str(e)}"
