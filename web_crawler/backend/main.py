"""Main FastAPI application - Orchestrates multi-agent ranking system."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import os
from typing import Optional
from io import StringIO, BytesIO
import pandas as pd
from datetime import datetime

# Import agents
from agents.planning_agent import PlanningAgent
from agents.research_agent import ResearchAgent
from agents.scoring_agent import ScoringAgent

# Import config
from config.state import RankingState
from config.settings import SOURCE_CONFIGS

# Import utils
from utils.helpers import (
    extract_urls, 
    parse_source_selection, 
    generate_chat_id,
    format_time_ago
)

# Initialize LLM
from langchain_groq import ChatGroq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    groq_api_key=GROQ_API_KEY
)

# Initialize agents
planning_agent = PlanningAgent(llm)
research_agent = ResearchAgent(llm)
scoring_agent = ScoringAgent(llm)

# FastAPI app
app = FastAPI(title="Multi-Agent Ranking System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class StartRequest(BaseModel):
    message: str

class ReplyRequest(BaseModel):
    message: str

class RefreshRequest(BaseModel):
    pass

# In-memory chat storage
chats = {}

# Serve frontend (if available)
try:
    app.mount("/static", StaticFiles(directory="../frontend/dist", html=True), name="frontend_static")
    
    @app.get("/")
    def serve_index():
        return FileResponse("../frontend/dist/index.html")
except Exception:
    pass

@app.post("/start")
def start_chat(req: StartRequest):
    """Start a new ranking conversation."""
    try:
        # Initialize state
        state: RankingState = {
            "query": req.message,
            "messages": [],
            "stage": "analyzing_query",
            "errors": []
        }
        
        # Planning Agent: Analyze query
        state = planning_agent.analyze_query(state)
        
        chat_id = generate_chat_id()
        chats[chat_id] = {
            "id": chat_id,
            "query": req.message,
            "state": state,
            "stage": "awaiting_metric_input",
            "messages": [{"role": "user", "text": req.message}]
        }
        
        domain = state.get("domain", "general")
        entity = state.get("entity_type", "items")
        region = state.get("region")
        
        prompt = (
            f"I understand you want a ranking of **{entity}**"
            f"{' in ' + region if region else ''} (domain: {domain}). "
            "\n\nWhat metrics would you like to use for ranking? "
            "You can specify your own (e.g., 'popularity, quality, impact') "
            "or say 'suggest metrics' and I'll provide options."
        )
        
        chats[chat_id]["messages"].append({"role": "assistant", "text": prompt})
        
        title = f"{entity}"
        if region:
            title = f"{title} ({region})"
        
        return {
            "ok": True,
            "chat_id": chat_id,
            "bot": prompt,
            "title": title,
            "messages": chats[chat_id]["messages"]
        }
        
    except Exception as e:
        return {"ok": False, "error": str(e), "trace": traceback.format_exc()}

@app.post("/chat/{chat_id}/reply")
def chat_reply(chat_id: str, req: ReplyRequest):
    """Handle replies in an existing chat."""
    try:
        if chat_id not in chats:
            return {"ok": False, "error": "chat_id not found"}
        
        chat = chats[chat_id]
        chat["messages"].append({"role": "user", "text": req.message})
        
        state = chat["state"]
        current_stage = chat.get("stage")
        
        # Stage 1: Awaiting metric input
        if current_stage == "awaiting_metric_input":
            return handle_metric_input(chat, req.message)
        
        # Stage 2: Awaiting metric selection (after suggestions)
        elif current_stage == "awaiting_metric_selection":
            return handle_metric_selection(chat, req.message)
        
        # Stage 3: Awaiting source selection
        elif current_stage == "awaiting_sources":
            return handle_source_selection(chat, req.message)
        
        # Stage 4: Awaiting custom URLs
        elif current_stage == "awaiting_custom_urls":
            return handle_custom_urls(chat, req.message)
        
        # Stage 5: Completed - handle insights
        elif current_stage == "completed":
            return handle_insight_query(chat, req.message)
        
        # Stage 6: Awaiting refresh confirmation
        elif current_stage == "awaiting_refresh":
            return handle_refresh_confirmation(chat, req.message)
        
        return {"ok": False, "error": f"Unknown stage: {current_stage}"}
        
    except Exception as e:
        return {"ok": False, "error": str(e), "trace": traceback.format_exc()}

def handle_metric_input(chat: dict, message: str) -> dict:
    """Handle initial metric input from user."""
    state = chat["state"]
    
    if any(word in message.lower() for word in ['suggest', 'recommend', 'help', 'ideas', 'options']):
        # User wants suggestions - Planning Agent selects metrics
        state = planning_agent.select_metrics(state)
        chat["state"] = state
        chat["stage"] = "awaiting_metric_selection"
        
        metrics = state.get("metrics", [])
        weights = state.get("weights", {})
        
        metric_list = []
        for i, metric in enumerate(metrics, 1):
            weight = weights.get(metric, 0)
            metric_display = metric.replace('_', ' ').title()
            metric_list.append(f"{i}. **{metric_display}** (weight: {weight:.2f})")
        
        suggestion_text = (
            f"Here are my suggested metrics for ranking {state.get('entity_type')}:\n\n" +
            "\n".join(metric_list) +
            "\n\n**Options:**\n" +
            "• Accept these metrics (say 'accept' or 'looks good')\n" +
            "• Remove specific metrics (e.g., 'remove metric 2')\n" +
            "• Provide your own (e.g., 'use popularity, quality, and impact')"
        )
        
        chat["messages"].append({"role": "assistant", "text": suggestion_text})
        
        return {
            "ok": True,
            "bot_text": suggestion_text,
            "suggested_metrics": [
                {"name": m, "weight": weights.get(m, 0), "display": m.replace('_', ' ').title()}
                for m in metrics
            ],
            "messages": chat["messages"]
        }
    else:
        # User specified custom metrics
        custom_metrics, custom_weights = planning_agent.parse_custom_metrics(message)
        
        if custom_metrics:
            state["metrics"] = custom_metrics
            state["weights"] = custom_weights
            chat["state"] = state
            
            return proceed_to_source_selection(chat)
        else:
            clarify = "I didn't quite catch which metrics you'd like. Could you list them or ask me to suggest some?"
            chat["messages"].append({"role": "assistant", "text": clarify})
            return {"ok": True, "bot_text": clarify, "messages": chat["messages"]}

def handle_metric_selection(chat: dict, message: str) -> dict:
    """Handle metric selection/modification after suggestions."""
    state = chat["state"]
    message_lower = message.lower()
    
    # User accepts suggested metrics
    if any(word in message_lower for word in ['accept', 'good', 'yes', 'okay', 'ok', 'perfect']):
        return proceed_to_source_selection(chat)
    
    # User wants to remove metrics
    elif 'remove' in message_lower or 'without' in message_lower:
        current_metrics = state.get("metrics", [])
        remove_indices = []
        
        for i in range(len(current_metrics)):
            if str(i+1) in message or current_metrics[i] in message_lower:
                remove_indices.append(i)
        
        new_metrics = [m for i, m in enumerate(current_metrics) if i not in remove_indices]
        
        if new_metrics and len(new_metrics) >= 2:
            w = 1.0 / len(new_metrics)
            new_weights = {m: round(w, 3) for m in new_metrics}
            
            state["metrics"] = new_metrics
            state["weights"] = new_weights
            chat["state"] = state
            
            metrics_descr = ", ".join([m.replace('_', ' ').title() for m in new_metrics])
            confirmation = f"Updated! I'll use: **{metrics_descr}**. Does this look good?"
            
            chat["messages"].append({"role": "assistant", "text": confirmation})
            
            return {
                "ok": True,
                "bot_text": confirmation,
                "suggested_metrics": [
                    {"name": m, "weight": new_weights.get(m, 0), "display": m.replace('_', ' ').title()}
                    for m in new_metrics
                ],
                "messages": chat["messages"]
            }
        else:
            error_msg = "You need at least 2 metrics. Which ones would you like to keep?"
            chat["messages"].append({"role": "assistant", "text": error_msg})
            return {"ok": True, "bot_text": error_msg, "messages": chat["messages"]}
    
    # User provides custom metrics
    else:
        custom_metrics, custom_weights = planning_agent.parse_custom_metrics(message)
        
        if custom_metrics:
            state["metrics"] = custom_metrics
            state["weights"] = custom_weights
            chat["state"] = state
            
            return proceed_to_source_selection(chat)
        else:
            clarify = "I didn't understand. Accept current metrics or specify your own."
            chat["messages"].append({"role": "assistant", "text": clarify})
            return {"ok": True, "bot_text": clarify, "messages": chat["messages"]}

def proceed_to_source_selection(chat: dict) -> dict:
    """Move to source selection stage."""
    state = chat["state"]
    chat["stage"] = "awaiting_sources"
    
    metrics_descr = ", ".join([m.replace('_', ' ').title() for m in state.get("metrics", [])])
    
    # Get source recommendations from Planning Agent
    source_info = planning_agent.recommend_sources(state)
    source_options = source_info["source_options"]
    
    ask_sources = (
        f"Perfect! I'll use these metrics: **{metrics_descr}**.\n\n"
        "Now, which sources should I use for data collection?\n\n"
        "I've recommended the best sources for this domain (marked with ⭐):"
    )
    
    chat["messages"].append({"role": "assistant", "text": ask_sources})
    
    return {
        "ok": True,
        "bot_text": ask_sources,
        "source_options": source_options,
        "messages": chat["messages"]
    }

def handle_source_selection(chat: dict, message: str) -> dict:
    """Handle source selection from user."""
    state = chat["state"]
    message_lower = message.lower()
    
    # Check if user selected "auto"
    if 'auto' in message_lower or 'recommend' in message_lower or 'choose for me' in message_lower:
        state['source_types'] = ['auto']
        state['explicit_source_urls'] = None
        return run_ranking_pipeline(chat)
    
    # Check if user wants custom URLs
    elif 'custom' in message_lower or 'my own' in message_lower or 'provide' in message_lower:
        urls = extract_urls(message)
        if urls:
            state['explicit_source_urls'] = urls
            state['source_types'] = ['custom']
            return run_ranking_pipeline(chat)
        else:
            chat["stage"] = "awaiting_custom_urls"
            ask_urls = "Please paste the URLs you'd like me to use (one per line or comma-separated)."
            chat["messages"].append({"role": "assistant", "text": ask_urls})
            return {"ok": True, "bot_text": ask_urls, "messages": chat["messages"]}
    
    # Parse specific source types
    else:
        available_sources = list(SOURCE_CONFIGS.keys())
        selected_sources = parse_source_selection(message, available_sources)
        
        if selected_sources:
            state['source_types'] = selected_sources
            state['explicit_source_urls'] = None
            return run_ranking_pipeline(chat)
        else:
            # Try to extract URLs anyway
            urls = extract_urls(message)
            if urls:
                state['explicit_source_urls'] = urls
                state['source_types'] = ['custom']
                return run_ranking_pipeline(chat)
            else:
                clarify = "I didn't quite catch which sources. You can say 'auto', select specific types, or provide URLs."
                chat["messages"].append({"role": "assistant", "text": clarify})
                return {"ok": True, "bot_text": clarify, "messages": chat["messages"]}

def handle_custom_urls(chat: dict, message: str) -> dict:
    """Handle custom URL input."""
    urls = extract_urls(message)
    
    if urls:
        chat["state"]['explicit_source_urls'] = urls
        chat["state"]['source_types'] = ['custom']
        return run_ranking_pipeline(chat)
    else:
        error_msg = "I didn't find any URLs. Please paste them (e.g., https://example.com)"
        chat["messages"].append({"role": "assistant", "text": error_msg})
        return {"ok": True, "bot_text": error_msg, "messages": chat["messages"]}

def run_ranking_pipeline(chat: dict) -> dict:
    """Execute the full ranking pipeline with all agents."""
    state = chat["state"]
    chat["stage"] = "running_pipeline"
    
    # Research Agent: Generate candidates
    state = research_agent.generate_candidates(state)
    
    # Research Agent: Collect data from sources
    state = research_agent.collect_data(state)
    
    # Scoring Agent: Score candidates
    state = scoring_agent.score_candidates(state)
    
    # Scoring Agent: Generate ranking
    state = scoring_agent.generate_ranking(state)
    
    # Scoring Agent: Detect changes (if previous scores exist)
    if state.get("previous_scores"):
        state = scoring_agent.detect_changes(state)
    
    chat["state"] = state
    chat["stage"] = "completed"
    
    # Build response
    table = state.get("final_table")
    metrics_descr = ", ".join([m.replace('_', ' ').title() for m in state.get("metrics", [])])
    num_items = state.get("num_items", 10)
    total_available = state.get("total_available", num_items)
    
    bot_text = f"✅ Here's your top {num_items} ranking of **{state.get('entity_type')}** using: **{metrics_descr}**"
    
    # Add source information
    source_types = state.get("source_types", [])
    if source_types and source_types != ['auto']:
        source_names = [SOURCE_CONFIGS[st]["name"] for st in source_types if st in SOURCE_CONFIGS]
        bot_text += f"\n\n📚 **Sources used:** {', '.join(source_names)}"
    
    # Add change information if detected
    change_summary = scoring_agent.generate_change_summary(state)
    if change_summary:
        bot_text += f"\n\n{change_summary}"
    
    # Add download prompt
    if total_available > num_items:
        bot_text += f"\n\n💡 I generated {total_available} items total. Use the download buttons to get the complete ranking!"
    
    # Add freshness indicator
    if state.get("last_updated"):
        bot_text += f"\n\n🕒 Data freshness: {format_time_ago(state['last_updated'])}"
    
    chat["messages"].append({"role": "assistant", "text": bot_text})
    
    # Prepare table data
    rows = None
    columns = None
    sources_info = None
    
    if table is not None:
        rows = table.to_dict(orient='records')
        columns = list(table.columns)
        
        # Prepare source information for transparency
        source_map = state.get("source_map", {})
        sources_info = {
            candidate: sources
            for candidate, sources in source_map.items()
            if candidate in [row['Name'] for row in rows]
        }
    
    return {
        "ok": True,
        "bot_text": bot_text,
        "columns": columns,
        "rows": rows,
        "sources": sources_info,
        "num_items": num_items,
        "total_available": total_available,
        "last_updated": state.get("last_updated").isoformat() if state.get("last_updated") else None,
        "messages": chat["messages"]
    }

def handle_insight_query(chat: dict, message: str) -> dict:
    """Handle insight queries about completed rankings."""
    state = chat["state"]
    
    # Check if user wants to refresh data
    if any(word in message.lower() for word in ['refresh', 'update', 'reload', 'latest', 'current']):
        chat["stage"] = "awaiting_refresh"
        confirm_msg = (
            "🔄 Would you like me to refresh the ranking with the latest data? "
            "This will re-check all sources and update the scores.\n\n"
            "Reply 'yes' to refresh or 'no' to continue with current data."
        )
        chat["messages"].append({"role": "assistant", "text": confirm_msg})
        return {"ok": True, "bot_text": confirm_msg, "messages": chat["messages"]}
    
    # Generate insight using LLM
    bot_text, cols, rows = generate_humanized_insight(state, message)
    chat["messages"].append({"role": "assistant", "text": bot_text})
    
    return {
        "ok": True,
        "bot_text": bot_text,
        "columns": cols,
        "rows": rows,
        "messages": chat["messages"]
    }

def handle_refresh_confirmation(chat: dict, message: str) -> dict:
    """Handle confirmation for data refresh."""
    if any(word in message.lower() for word in ['yes', 'sure', 'ok', 'yeah', 'refresh']):
        # Save previous scores for change detection
        chat["state"]["previous_scores"] = chat["state"].get("scores", {})
        
        # Re-run the pipeline
        return run_ranking_pipeline(chat)
    else:
        chat["stage"] = "completed"
        bot_text = "Okay, continuing with current data. What would you like to know?"
        chat["messages"].append({"role": "assistant", "text": bot_text})
        return {"ok": True, "bot_text": bot_text, "messages": chat["messages"]}

def generate_humanized_insight(state: dict, user_question: str) -> tuple:
    """Generate conversational insights about the ranking."""
    df = state.get("final_table")
    if df is None:
        return ("I don't have a ranking table yet to analyze.", None, None)
    
    table_context = df.to_string(index=False)
    metrics = state.get("metrics", [])
    entity_type = state.get("entity_type", "items")
    
    prompt = f"""You are a friendly data analyst. Answer the user's question about this ranking.

Entity Type: {entity_type}
Metrics: {', '.join(metrics)}

Ranking Table:
{table_context}

User Question: "{user_question}"

Provide a conversational, insightful answer with specific data points.
If showing table data, indicate "SHOW_TABLE: true" and row indices (comma-separated).
Otherwise, indicate "SHOW_TABLE: false"
"""
    
    try:
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        show_table = False
        row_indices = []
        insight_text = content
        
        if "SHOW_TABLE:" in content:
            parts = content.split("SHOW_TABLE:")
            insight_text = parts[0].strip()
            table_instruction = parts[1].strip()
            
            if "true" in table_instruction.lower():
                show_table = True
                import re
                indices_match = re.search(r'(\d+(?:,\d+)*)', table_instruction)
                if indices_match:
                    row_indices = [int(i) for i in indices_match.group(1).split(',')]
        
        if show_table and row_indices:
            filtered_df = df[df['Rank'].isin([i+1 for i in row_indices])]
            return (insight_text, list(filtered_df.columns), filtered_df.to_dict(orient='records'))
        elif show_table:
            return (insight_text, list(df.columns), df.to_dict(orient='records'))
        else:
            return (insight_text, None, None)
            
    except Exception as e:
        print(f"Error generating insight: {e}")
        return (f"Looking at the data, there are interesting patterns. Could you rephrase your question?", None, None)

@app.get("/chat/{chat_id}/messages")
def get_messages(chat_id: str):
    """Get all messages for a chat."""
    if chat_id not in chats:
        return {"ok": False, "error": "chat_id not found"}
    
    return {
        "ok": True,
        "messages": chats[chat_id]["messages"]
    }

@app.get("/chat/{chat_id}/sources")
def get_sources(chat_id: str):
    """Get detailed source information for a ranking."""
    if chat_id not in chats:
        return {"ok": False, "error": "chat_id not found"}
    
    source_map = chats[chat_id]["state"].get("source_map", {})
    
    return {
        "ok": True,
        "sources": source_map,
        "last_updated": chats[chat_id]["state"].get("last_updated")
    }

@app.post("/chat/{chat_id}/refresh")
def refresh_ranking(chat_id: str):
    """Manually refresh the ranking with latest data."""
    if chat_id not in chats:
        return {"ok": False, "error": "chat_id not found"}
    
    chat = chats[chat_id]
    
    if chat.get("stage") != "completed":
        return {"ok": False, "error": "Ranking not yet completed"}
    
    # Save previous scores
    chat["state"]["previous_scores"] = chat["state"].get("scores", {})
    
    # Re-run pipeline
    result = run_ranking_pipeline(chat)
    
    return result

@app.get("/chat/{chat_id}/download")
def download_table(chat_id: str, format: str = "csv"):
    """Download the ranking table."""
    if chat_id not in chats:
        return {"ok": False, "error": "chat_id not found"}
    
    df = chats[chat_id]["state"].get("full_table")
    if df is None:
        df = chats[chat_id]["state"].get("final_table")
    
    if df is None:
        return {"ok": False, "error": "No table available"}
    
    if "Rank" not in df.columns:
        df_copy = df.copy()
        df_copy.index = df_copy.index + 1
        df_copy.insert(0, "Rank", df_copy.index)
    else:
        df_copy = df.copy()
    
    filename = f"ranking_{chat_id[:8]}"
    
    if format == "csv":
        buffer = StringIO()
        df_copy.to_csv(buffer, index=False)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"}
        )
    
    elif format == "xlsx":
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_copy.to_excel(writer, index=False, sheet_name="Ranking")
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"}
        )
    
    return {"ok": False, "error": "Invalid format (use csv or xlsx)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)