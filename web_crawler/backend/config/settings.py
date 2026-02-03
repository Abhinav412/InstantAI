"""Configuration settings for the ranking system."""

from typing import Dict, List
from enum import Enum

class SourceType(Enum):
    """Available source types for data collection."""
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    ACADEMIC = "academic"
    INDUSTRY_REPORTS = "industry_reports"
    OFFICIAL_STATS = "official_stats"
    FORUMS = "forums"
    REVIEWS = "reviews"
    CUSTOM_URLS = "custom_urls"
    AUTO = "auto"  # Let the system decide

# Source configurations with search patterns
SOURCE_CONFIGS: Dict[str, Dict] = {
    "news": {
        "name": "News Articles",
        "description": "Recent news from major publications",
        "domains": ["cnn.com", "bbc.com", "reuters.com", "apnews.com", "theguardian.com"],
        "search_suffix": "news",
        "icon": "📰"
    },
    "social_media": {
        "name": "Social Media",
        "description": "Twitter/X, Reddit, and social platforms",
        "domains": ["twitter.com", "reddit.com", "x.com"],
        "search_suffix": "reddit OR twitter",
        "icon": "💬"
    },
    "academic": {
        "name": "Academic Sources",
        "description": "Research papers and academic publications",
        "domains": ["scholar.google.com", "arxiv.org", "jstor.org"],
        "search_suffix": "research paper OR study",
        "icon": "🎓"
    },
    "industry_reports": {
        "name": "Industry Reports",
        "description": "Market research and industry analysis",
        "domains": ["statista.com", "gartner.com", "forrester.com"],
        "search_suffix": "market report OR industry analysis",
        "icon": "📊"
    },
    "official_stats": {
        "name": "Official Statistics",
        "description": "Government and official organization data",
        "domains": [".gov", "who.int", "worldbank.org", "imf.org"],
        "search_suffix": "official statistics",
        "icon": "🏛️"
    },
    "forums": {
        "name": "Community Forums",
        "description": "Discussion forums and Q&A sites",
        "domains": ["stackoverflow.com", "hackernews.com", "quora.com"],
        "search_suffix": "forum discussion",
        "icon": "💭"
    },
    "reviews": {
        "name": "Reviews & Ratings",
        "description": "User reviews and rating platforms",
        "domains": ["yelp.com", "trustpilot.com", "g2.com", "capterra.com"],
        "search_suffix": "reviews ratings",
        "icon": "⭐"
    },
    "auto": {
        "name": "Auto Select",
        "description": "System automatically selects best sources",
        "domains": [],
        "search_suffix": "",
        "icon": "🤖"
    }
}

# Domain-specific source recommendations
DOMAIN_SOURCE_RECOMMENDATIONS: Dict[str, List[str]] = {
    "gaming": ["social_media", "forums", "reviews", "news"],
    "esports": ["news", "social_media", "official_stats"],
    "technology": ["news", "industry_reports", "academic", "reviews"],
    "entertainment": ["news", "social_media", "reviews"],
    "sports": ["news", "official_stats", "social_media"],
    "business": ["news", "industry_reports", "official_stats"],
    "finance": ["news", "official_stats", "industry_reports"],
    "education": ["academic", "official_stats", "reviews"],
    "health": ["academic", "official_stats", "news"],
    "food": ["reviews", "social_media", "news"],
    "travel": ["reviews", "news", "social_media"],
    "default": ["news", "social_media", "reviews"]
}

# Rate limiting and caching settings
RATE_LIMIT_DELAY = 2  # seconds between requests
CACHE_DURATION = 3600  # 1 hour in seconds
MAX_SOURCES_PER_CANDIDATE = 5
REQUEST_TIMEOUT = 15  # seconds

# LLM Settings
DEFAULT_TEMPERATURE = 0.7
MAX_RETRIES = 3

# Dynamic ranking settings
DYNAMIC_RANKING_ENABLED = True
CHANGE_DETECTION_THRESHOLD = 0.1  # 10% change in score
UPDATE_CHECK_INTERVAL = 3600  # Check for updates every hour