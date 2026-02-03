"""Planning Agent - Analyzes queries and plans the ranking strategy."""

from typing import Dict, List, Optional, Tuple
import json
import re
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from config.state import RankingState, AgentOutput
from config.settings import DOMAIN_SOURCE_RECOMMENDATIONS, SOURCE_CONFIGS

class PlanningAgent:
    """Agent responsible for understanding the query and planning the ranking approach."""
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        
    def analyze_query(self, state: RankingState) -> RankingState:
        """Analyze the user query to extract domain, entity type, region, time scope, and number of items."""
        query = state.get("query", "")
        
        prompt = f"""You are an expert at analyzing ranking requests across ALL domains. Analyze this query and extract the key information.

CRITICAL INSTRUCTIONS FOR ENTITY RECOGNITION:
1. **Preserve Full Context**: The entity_type should capture the COMPLETE context from the query
   - "clash royale players" → entity_type: "clash royale players" (NOT just "players")
   - "best restaurants in Paris" → entity_type: "restaurants" + region: "Paris"
   - "top python libraries" → entity_type: "python libraries" (NOT just "libraries")

2. **Domain Recognition**: Identify the broader category
   - Gaming/Esports, Technology, Entertainment, Sports, Business, Food/Dining, 
     Education, Health, Finance, Travel, etc.

3. **Extract Time Context**: Identify if query asks for current, recent, or specific time period
   - "current", "latest", "2024", "this year", "recent" → capture in time_scope

Query: {query}

Return ONLY a JSON object with these keys: domain, entity_type, region, time_scope, num_items

Example: {{"domain": "gaming", "entity_type": "clash royale players", "region": null, "time_scope": "current", "num_items": 10}}
"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            content = self._clean_json(response.content)
            result = json.loads(content)
            
            state["domain"] = result.get("domain", "general")
            state["entity_type"] = result.get("entity_type")
            state["region"] = result.get("region")
            state["time_scope"] = result.get("time_scope")
            state["num_items"] = result.get("num_items", 10)
            
            print(f"✓ Query Analysis - Domain: {state['domain']}, Entity: {state['entity_type']}")
            
        except Exception as e:
            print(f"✗ Error in query analysis: {e}")
            state = self._fallback_analysis(query, state)
            
        return state
    
    def select_metrics(self, state: RankingState) -> RankingState:
        """Select appropriate ranking metrics based on domain and entity type."""
        domain = state.get("domain", "general")
        entity_type = state.get("entity_type", "items")
        
        prompt = f"""Generate 3-5 highly relevant ranking metrics for evaluating "{entity_type}" in the "{domain}" domain.

METRIC SELECTION PRINCIPLES:
1. Metrics must be SPECIFIC and MEASURABLE
2. Consider what makes one entity "better" than another
3. Use a mix of objective and qualitative metrics
4. Should differentiate between entities effectively

For "{entity_type}" in "{domain}":
Return ONLY a JSON object with:
- "metrics": list of 3-5 metric names (lowercase, underscore-separated)
- "weights": object mapping each metric to a weight (sum to 1.0)
- "reasoning": brief explanation of why these metrics

Example: {{"metrics": ["skill_rating", "tournament_wins", "consistency"], "weights": {{"skill_rating": 0.4, "tournament_wins": 0.35, "consistency": 0.25}}, "reasoning": "These metrics capture both performance and reliability"}}
"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            content = self._clean_json(response.content)
            result = json.loads(content)
            
            state["metrics"] = result.get("metrics", ["quality", "popularity", "relevance"])
            state["weights"] = result.get("weights", {})
            
            print(f"✓ Selected metrics: {', '.join(state['metrics'])}")
            
        except Exception as e:
            print(f"✗ Error selecting metrics: {e}")
            state = self._fallback_metrics(domain, state)
            
        return state
    
    def recommend_sources(self, state: RankingState) -> Dict[str, any]:
        """Recommend source types based on domain and entity type."""
        domain = state.get("domain", "general")
        entity_type = state.get("entity_type", "items")
        
        # Get domain-specific recommendations
        recommended_types = DOMAIN_SOURCE_RECOMMENDATIONS.get(
            domain.lower(), 
            DOMAIN_SOURCE_RECOMMENDATIONS["default"]
        )
        
        # Build source options for user
        source_options = []
        for source_type in recommended_types:
            if source_type in SOURCE_CONFIGS:
                config = SOURCE_CONFIGS[source_type]
                source_options.append({
                    "id": source_type,
                    "name": config["name"],
                    "description": config["description"],
                    "icon": config["icon"],
                    "recommended": True
                })
        
        # Add other sources as non-recommended
        for source_type, config in SOURCE_CONFIGS.items():
            if source_type not in recommended_types and source_type != "auto":
                source_options.append({
                    "id": source_type,
                    "name": config["name"],
                    "description": config["description"],
                    "icon": config["icon"],
                    "recommended": False
                })
        
        # Add auto and custom options
        source_options.insert(0, {
            "id": "auto",
            "name": "Auto Select (Recommended)",
            "description": f"I'll pick the best sources for {entity_type}",
            "icon": "🤖",
            "recommended": True
        })
        
        source_options.append({
            "id": "custom",
            "name": "Custom URLs",
            "description": "Provide specific URLs to use",
            "icon": "🔗",
            "recommended": False
        })
        
        return {
            "source_options": source_options,
            "recommended_count": len([s for s in source_options if s.get("recommended")])
        }
    
    def parse_custom_metrics(self, user_message: str) -> Tuple[Optional[List[str]], Optional[Dict[str, float]]]:
        """Parse user's custom metrics from natural language."""
        auto_keywords = ["pick", "choose", "auto", "you decide", "you choose", "your choice", "select for me"]
        if any(keyword in user_message.lower() for keyword in auto_keywords):
            return None, None
        
        prompt = f"""Extract ranking metrics from this message.

User message: "{user_message}"

If providing specific metrics, extract them and return:
{{"metrics": ["metric1", "metric2", ...], "wants_auto": false}}

If asking you to choose, return:
{{"wants_auto": true}}

Return ONLY valid JSON.
"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            content = self._clean_json(response.content)
            result = json.loads(content)
            
            if result.get("wants_auto"):
                return None, None
            
            metrics = result.get("metrics", [])[:5]
            if metrics:
                w = 1.0 / len(metrics)
                weights = {m: round(w, 3) for m in metrics}
                return metrics, weights
                
        except Exception as e:
            print(f"Error parsing custom metrics: {e}")
            
        return None, None
    
    def _clean_json(self, content: str) -> str:
        """Clean JSON from markdown code blocks."""
        content = content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return content
    
    def _fallback_analysis(self, query: str, state: RankingState) -> RankingState:
        """Fallback query analysis using regex."""
        query_lower = query.lower()
        
        # Extract number
        num_match = re.search(r'\b(top|best|first)\s+(\d+)\b', query_lower)
        num_items = int(num_match.group(2)) if num_match else 10
        
        # Extract entity
        stop_words = ['top', 'best', 'rank', 'the', 'a', 'an', 'in', 'of', 'for', 'by']
        words = query_lower.split()
        entity_words = [w for w in words if w not in stop_words and not w.isdigit()]
        entity_type = ' '.join(entity_words) if entity_words else "items"
        
        state["domain"] = "general"
        state["entity_type"] = entity_type
        state["region"] = None
        state["time_scope"] = None
        state["num_items"] = num_items
        
        return state
    
    def _fallback_metrics(self, domain: str, state: RankingState) -> RankingState:
        """Fallback metric selection based on domain."""
        domain_metrics = {
            "gaming": (["skill_level", "achievements", "popularity"], 
                      {"skill_level": 0.4, "achievements": 0.35, "popularity": 0.25}),
            "technology": (["innovation", "market_impact", "adoption"], 
                          {"innovation": 0.35, "market_impact": 0.35, "adoption": 0.3}),
            "entertainment": (["critical_acclaim", "popularity", "cultural_impact"], 
                            {"critical_acclaim": 0.35, "popularity": 0.35, "cultural_impact": 0.3}),
        }
        
        metrics, weights = domain_metrics.get(domain, 
            (["quality", "popularity", "relevance"], 
             {"quality": 0.33, "popularity": 0.33, "relevance": 0.34}))
        
        state["metrics"] = metrics
        state["weights"] = weights
        
        return state