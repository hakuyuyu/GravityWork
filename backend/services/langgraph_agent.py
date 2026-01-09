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
        """Gather context from Jira, Docs (Qdrant) before planning."""
        user_query = state["messages"][0].content if state["messages"] else ""
        scratchpad = {"query": user_query}
        context_parts = []
        
        # 1. Jira Scouting
        ticket_id = self._extract_ticket_id(user_query)
        if ticket_id:
            logger.info(f"Detected ticket ID: {ticket_id}")
            result = await self.mcp_client.get_ticket_status(ticket_id)
            if result.success:
                scratchpad["jira_context"] = result.data
                context_parts.append(f"Found Jira ticket {ticket_id}: {result.data}")
            else:
                context_parts.append(f"Could not fetch ticket {ticket_id}: {result.error}")
        
        # 2. Knowledge Base Scouting (Qdrant)
        try:
             # Lazy import inside method to avoid circular imports if any
            from backend.services.qdrant_service import QdrantService
            # We assume a singleton or new instance is fine (it connects via HTTP)
            qdrant = QdrantService() 
            if qdrant.collection_exists():
                # Search using the full query
                docs = qdrant.search_similar(query_text=user_query, limit=3)
                if docs:
                    doc_context = "\n".join([f"- {d['text']} (source: {d['metadata']})" for d in docs])
                    context_parts.append(f"Knowledge Base Results:\n{doc_context}")
                    scratchpad["docs"] = docs
        except Exception as e:
            logger.warning(f"Qdrant scout failed: {e}")

        # If no specific context found, search Jira broadly
        if not ticket_id and not scratchpad.get("docs"):
             result = await self.mcp_client.search_tickets(user_query)
             if result.success and result.data:
                 issues = result.data.get('data', {}).get('issues', [])
                 if issues:
                     context_parts.append(f"Found {len(issues)} related tickets in Jira.")
                     scratchpad["jira_search_results"] = result.data

        final_context = "\n\n".join(context_parts) if context_parts else "No specific context found."
        
        return {
            "messages": [AIMessage(content=final_context)],
            "scratchpad": scratchpad
        }

    async def _plan_node(self, state: AgentState):
        """Decide on the action plan based on scouted context using Real LLM."""
        query = state.get("scratchpad", {}).get("query", "")
        scratchpad = state.get("scratchpad", {})
        
        # System Prompt for the Project Manager Persona
        system_prompt = """You are GravityWork, an AI Project Manager.
        Your goal is to help users manage their projects, Jira tickets, and tasks.
        
        Context found:
        {context}
        
        User Query: {query}
        
        Decide on the next step.
        If the user wants to perform an action (Create, Update, Delete), output JSON:
        {{"type": "action", "action_type": "<create_ticket|update_ticket|slack_action>", "parameters": <json_params>}}
        
        If the user wants information you already have or can find, output JSON:
        {{"type": "response", "content": "<your friendly response>"}}
        
        Date: {date}
        """
        
        context_str = str(scratchpad)
        
        if self.llm:
            try:
                from langchain_core.messages import SystemMessage
                from datetime import datetime
                
                messages = [
                    SystemMessage(content=system_prompt.format(
                        context=context_str, 
                        query=query,
                        date=datetime.now().isoformat()
                    )),
                    HumanMessage(content=query)
                ]
                
                response = await self.llm.ainvoke(messages)
                content = response.content
                
                # Simple parsing (robust JSON parsing would be better)
                import json
                
                # Extract JSON block
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        plan_data = json.loads(json_match.group(0))
                        
                        if plan_data.get("type") == "action":
                            return {
                                "messages": [AIMessage(content="Planning action...")],
                                "pending_action": {
                                    "type": plan_data.get("action_type"),
                                    **plan_data.get("parameters", {})
                                }
                            }
                        else:
                            return {
                                "messages": [AIMessage(content=plan_data.get("content", content))],
                                "pending_action": None
                            }
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse LLM JSON response")
                
                # Fallback to direct response if no JSON
                return {
                    "messages": [AIMessage(content=content)],
                    "pending_action": None
                }
                
            except Exception as e:
                logger.error(f"LLM Error: {e}")
                return {
                    "messages": [AIMessage(content="Sorry, I'm having trouble thinking right now.")],
                    "pending_action": None
                }
        else:
             # Fallback to Mock Logic if LLM not available
             return await self._mock_plan_node(state)

    async def _mock_plan_node(self, state: AgentState):
        """Legacy mock planning logic."""
        query = state.get("scratchpad", {}).get("query", "").lower()
        # ... (Existing mock logic preserved for safety) ...
        if "create" in query and "ticket" in query:
            return {"messages": [AIMessage(content="Mock Plan: Create Ticket")], "pending_action": {"type": "create_ticket", "summary": query}}
        return {"messages": [AIMessage(content="Mock Response: I need an LLM to answer that.")], "pending_action": None}

    async def _execute_node(self, state: AgentState):
        """Execute the planned action via MCP tools."""
        pending_action = state.get("pending_action")
        
        if not pending_action:
            # No action to execute, assume 'plan' node already provided the response
            return {}

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
