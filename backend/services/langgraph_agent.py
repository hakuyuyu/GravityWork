from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import os
import operator

# Define Agent State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    scratchpad: dict

class LangGraphAgent:
    """
    Orchestrates complex tasks using LangGraph.
    """
    def __init__(self):
        # Initialize LLM (using OpenRouter/OpenAI compatible endpoint)
        self.llm = ChatOpenAI(
            model=os.getenv("MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        self.workflow = self._build_graph()

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
        # For now, just pass through. In future, query Qdrant/Jira here.
        return {"messages": [AIMessage(content="Scouting context...")]}

    async def _plan_node(self, state: AgentState):
        """Decide on the action plan."""
        # Simple planner
        return {"messages": [AIMessage(content="Planning action...")]}

    async def _execute_node(self, state: AgentState):
        """Execute the planned tools."""
        # Placeholder for tool execution
        return {"messages": [AIMessage(content="Executing action via MCP...")]}

    async def run(self, query: str):
        """Run the agent workflow."""
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "next_step": "scout",
            "scratchpad": {}
        }
        
        results = await self.workflow.ainvoke(initial_state)
        return results["messages"][-1].content
