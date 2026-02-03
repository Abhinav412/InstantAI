"""State definitions for the multi-agent ranking system."""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
import pandas as pd

class RankingState(TypedDict):
    """State shared across all agents in the ranking pipeline."""
    
    # Query analysis
    query: str
    domain: Optional[str]
    entity_type: Optional[str]
    region: Optional[str]
    time_scope: Optional[str]
    num_items: Optional[int]
    
    # Metrics
    metrics: Optional[List[str]]
    weights: Optional[Dict[str, float]]
    
    # Source selection
    source_types: Optional[List[str]]  # e.g., ['news', 'social_media']
    explicit_source_urls: Optional[List[str]]  # User-provided URLs
    selected_sources: Optional[Dict[str, List[str]]]  # candidate -> [urls]
    
    # Research data
    candidates: Optional[List[str]]
    raw_data: Optional[Dict[str, str]]  # candidate -> extracted text
    structured_data: Optional[Dict[str, Dict[str, Any]]]  # candidate -> metric data
    
    # Scoring
    scores: Optional[Dict[str, Dict[str, float]]]  # candidate -> {metric: score}
    previous_scores: Optional[Dict[str, Dict[str, float]]]  # For change detection
    
    # Results
    final_table: Optional[pd.DataFrame]
    full_table: Optional[pd.DataFrame]
    total_available: Optional[int]
    
    # Change tracking
    changes_detected: Optional[Dict[str, Dict[str, Any]]]  # candidate -> changes
    last_updated: Optional[datetime]
    
    # Source transparency
    source_map: Optional[Dict[str, List[Dict[str, str]]]]  # candidate -> [{url, title, source_type}]
    
    # Messages
    messages: List[Dict[str, str]]
    
    # Stage tracking
    stage: str
    errors: Optional[List[str]]


class AgentOutput(TypedDict):
    """Standard output format for all agents."""
    success: bool
    data: Optional[Any]
    message: str
    next_stage: Optional[str]
    sources_used: Optional[List[Dict[str, str]]]
    errors: Optional[List[str]]