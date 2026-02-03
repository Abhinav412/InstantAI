"""Utility functions for the ranking system."""

import re
from typing import List, Optional
from datetime import datetime, timedelta

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    if not text:
        return []
    return re.findall(r'https?://\S+', text)

def parse_source_selection(message: str, available_sources: List[str]) -> Optional[List[str]]:
    """Parse user's source selection from message."""
    message_lower = message.lower()
    
    # Check for "all" or "everything"
    if any(word in message_lower for word in ['all', 'everything', 'every']):
        return available_sources
    
    # Extract mentioned source types
    selected = []
    for source in available_sources:
        source_name = source.replace('_', ' ')
        if source in message_lower or source_name in message_lower:
            selected.append(source)
    
    return selected if selected else None

def format_metric_display(metric: str) -> str:
    """Format metric name for display."""
    return metric.replace('_', ' ').title()

def calculate_freshness_score(last_updated: datetime) -> float:
    """Calculate how fresh the data is (0-1, higher is fresher)."""
    if not last_updated:
        return 0.0
    
    age = datetime.now() - last_updated
    hours_old = age.total_seconds() / 3600
    
    # Fresh for first hour, decay over 24 hours
    if hours_old < 1:
        return 1.0
    elif hours_old < 24:
        return 1.0 - (hours_old - 1) / 23 * 0.5  # Decay to 0.5 over 24 hours
    else:
        return max(0.0, 0.5 - (hours_old - 24) / 168 * 0.5)  # Decay to 0 over week

def format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X minutes/hours/days ago'."""
    if not dt:
        return "Never"
    
    diff = datetime.now() - dt
    
    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        mins = int(diff.total_seconds() / 60)
        return f"{mins} minute{'s' if mins != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    return filename[:200]

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_percentage_change(old_value: float, new_value: float) -> str:
    """Format percentage change with arrow indicator."""
    if old_value == 0:
        return "N/A"
    
    change = ((new_value - old_value) / old_value) * 100
    arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
    
    return f"{arrow} {abs(change):.1f}%"

def generate_chat_id() -> str:
    """Generate a unique chat ID."""
    from uuid import uuid4
    return str(uuid4())

def validate_weights(weights: dict) -> bool:
    """Validate that weights sum to approximately 1.0."""
    if not weights:
        return False
    
    total = sum(weights.values())
    return 0.99 <= total <= 1.01

def normalize_weights(weights: dict) -> dict:
    """Normalize weights to sum to 1.0."""
    if not weights:
        return {}
    
    total = sum(weights.values())
    if total == 0:
        # Equal weights if all zero
        n = len(weights)
        return {k: 1.0/n for k in weights.keys()}
    
    return {k: v/total for k, v in weights.items()}