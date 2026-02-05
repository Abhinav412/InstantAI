"""Planning agent for the ranking app."""

import operator
from typing import Annotated, List, Literal, Optional, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph, add_messages
from pydantic import BaseModel, Field

from enrichment_agent import prompts
from enrichment_agent.configuration import Configuration
from enrichment_agent.utils import init_model


class ResearchSpec(BaseModel):
    """The final specification for the research task."""

    topic: str = Field(description="The main subject of research")
    depth: str = Field(description="depth of research: 'summary' or 'deep'")
    format: str = Field(description="Desired output format")
    preferences: str = Field(description="Any specific user constraints")


class PlanningState(BaseModel):
    """State for planning agent."""

    messages: Annotated[List[BaseMessage], add_messages]
    research_spec: Optional[ResearchSpec] = None


async def call_planner_model(state: PlanningState, config: RunnableConfig):
    """Calls the planner model to generate a research spec."""
    configuration = Configuration.from_runnable_config(config)

    current_spec = state.research_spec.model_dump() if state.research_spec else {}
    system_prompt = prompts.PLANNER_PROMPT.format(info=current_spec)

    messages = [HumanMessage(content=system_prompt)] + state.messages

    raw_model = init_model(config)
    model = raw_model.bind_tools([ResearchSpec], tool_choice="auto")

    response = await model.ainvoke(messages)
    return {"messages": [response]}


def route_planner(state: PlanningState) -> Literal["__end__", "wait_for_user"]:
    """Routes the planner based on the model response."""
    last_msg = state.messages[-1]

    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        tool_call = last_msg.tool_calls[0]
        if tool_call["name"] == "ResearchSpec":
            spec = ResearchSpec(**tool_call["args"])
            return "__end__"

    return "wait_for_user"


def process_spec(state: PlanningState):
    """Extracts the spec from the tool call to update state."""
    last_msg = state.messages[-1]
    tool_call = last_msg.tool_calls[0]
    spec = ResearchSpec(**tool_call["args"])
    return {"research_spec": spec}


workflow = StateGraph(PlanningState, config_schema=Configuration)
workflow.add_node("planner", call_planner_model)
workflow.add_node("process_spec", process_spec)
workflow.add_edge(START, "planner")
workflow.add_conditional_edges(
    "planner", route_planner, {"__end__": "process_spec", "wait_for_user": END}
)
workflow.add_edge("process_spec", END)
planning_graph = workflow.compile()
