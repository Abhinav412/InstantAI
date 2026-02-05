"""Research Agent."""

from typing import Annotated, List, Literal

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from enrichment_agent.configuration import Configuration
from enrichment_agent.tools import search
from enrichment_agent.tools.crawling import Crawl4AICrawler
from enrichment_agent.tools.storage import MongoWriter
from enrichment_agent.utils import init_model


class ResearchState(BaseModel):
    """Input State."""

    messages: Annotated[List[BaseMessage], add_messages]
    session_id: str
    spec: dict


async def call_research_model(state: ResearchState, config: RunnableConfig):
    """Call research model."""
    raw_model = init_model(config)
    tools = [search, Crawl4AICrawler(), MongoWriter()]

    p = (
        f"You are a Research Agent. Your goal is to research: {state.spec.get('topic')}. \n"
        f"Constraints: {state.spec.get('preferences')}.\n"
        f"Session ID: {state.session_id} (Pass this to the save tool).\n"
        "1. Search for relevant URLs.\n"
        "2. Crawl them to get details.\n"
        "3. Save useful findings to the DB using 'save_research_data'.\n"
        "Stop when you have sufficient information."
    )

    model = raw_model.bind_tools(tools)
    messages = [AIMessage(content=p)] + state.messages
    response = await model.ainvoke(messages)
    return {"messages": [response]}


def route_research(state: ResearchState) -> Literal["tools", "__end__"]:
    """Route research."""
    last_msg = state.messages[-1]
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return "tools"
    return "__end__"


workflow = StateGraph(ResearchState, config_schema=Configuration)
workflow.add_node("researcher", call_research_model)
workflow.add_node("tools", ToolNode([search, Crawl4AICrawler(), MongoWriter()]))

workflow.add_edge(START, "researcher")
workflow.add_conditional_edges("researcher", route_research)
workflow.add_edge("tools", "researcher")

research_graph = workflow.compile()
