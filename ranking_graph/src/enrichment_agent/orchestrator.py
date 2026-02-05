"""Orchestrator."""

import operator
from typing import Annotated, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph, add_messages
from pydantic import BaseModel

from enrichment_agent.agents.planning import ResearchSpec, planning_graph
from enrichment_agent.agents.research import research_graph
from enrichment_agent.configuration import Configuration
from enrichment_agent.db import save_research_session, update_session_status


class OrchestratorState(BaseModel):
    """Orchestrator State."""

    messages: Annotated[List[BaseMessage], add_messages]
    research_spec: Optional[ResearchSpec] = None
    session_id: Optional[str] = None
    research_results: Optional[List[BaseMessage]] = None


async def run_planning(state: OrchestratorState):
    """Run planning."""
    result = await planning_graph.ainvoke({"messages": state.messages})
    return {
        "messages": result["messages"],
        "research_spec": result.get("research_spec"),
    }


def create_session(state: OrchestratorState):
    """Create session."""
    if not state.research_spec:
        raise ValueError("Research Spec missing!")

    spec_data = state.research_spec.model_dump()
    session_id = save_research_session(
        user_id="default_user",
        topic=spec_data["topic"],
        preferences=spec_data,
    )
    return {"session_id": session_id}


async def run_research(state: OrchestratorState):
    """Run research."""
    inputs = {
        "messages": [],
        "session_id": state.session_id,
        "spec": state.research_spec.model_dump(),
    }
    result = await research_graph.ainvoke(inputs)

    update_session_status(state.session_id, "completed")

    return {"research_results": result["messages"]}


workflow = StateGraph(OrchestratorState, config_schema=Configuration)

workflow.add_node("planning", run_planning)
workflow.add_node("create_session", create_session)
workflow.add_node("research", run_research)

workflow.add_edge(START, "planning")
workflow.add_edge("planning", "create_session")
workflow.add_edge("create_session", "research")
workflow.add_edge("research", END)

orchestrator_graph = workflow.compile()
