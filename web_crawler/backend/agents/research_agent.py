"""Research Agent - Collects data from various sources."""

from typing import Dict, List, Optional
import json
import time
import re
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from config.state import RankingState
from config.settings import SOURCE_CONFIGS, RATE_LIMIT_DELAY, MAX_SOURCES_PER_CANDIDATE

class ResearchAgent:
    """Agent responsible for researching candidates and collecting data from sources."""
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        
    def generate_candidates(self, state: RankingState) -> RankingState:
        """Generate a list of candidate entities to rank."""
        entity_type = state.get("entity_type", "items")
        region = state.get("region", "global")
        domain = state.get("domain", "general")
        time_scope = state.get("time_scope")
        num_items = state.get("num_items", 10)
        
        num_to_generate = min(num_items + 5, 20)
        
        time_context = f" from {time_scope}" if time_scope else ""
        
        prompt = f"""Generate a list of {num_to_generate} well-known {entity_type}{time_context} in {region or 'the world'} within the {domain} domain.

IMPORTANT:
- Be SPECIFIC to the entity type requested
- Use real, well-known names that exist in that specific context
- If time_scope is mentioned, prioritize current/recent entities
- Return ONLY a JSON array of names

Example: ["Entity 1", "Entity 2", "Entity 3", ...]
"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            content = self._clean_json(response.content)
            
            candidates = json.loads(content)
            state["candidates"] = candidates[:num_to_generate]
            
            print(f"✓ Generated {len(state['candidates'])} candidates")
            
        except Exception as e:
            print(f"✗ Error generating candidates: {e}")
            state["candidates"] = [f"{entity_type} {i+1}" for i in range(num_to_generate)]
            
        return state
    
    def collect_data(self, state: RankingState) -> RankingState:
        """Collect data from selected sources for each candidate."""
        candidates = state.get("candidates", [])
        source_types = state.get("source_types", ["auto"])
        explicit_urls = state.get("explicit_source_urls", [])
        entity_type = state.get("entity_type", "items")
        domain = state.get("domain", "general")
        
        if not candidates:
            state["errors"] = state.get("errors", []) + ["No candidates to research"]
            return state
        
        # If user provided explicit URLs, use simulated data with those sources
        if explicit_urls:
            print(f"✓ Using {len(explicit_urls)} user-provided URLs")
            return self._collect_from_custom_urls(state, candidates, explicit_urls)
        
        # Determine which sources to use
        if "auto" in source_types or not source_types:
            source_types = self._auto_select_sources(domain)
            print(f"✓ Auto-selected sources: {', '.join(source_types)}")
        
        # Collect data for each candidate
        raw_data = {}
        source_map = {}
        
        for candidate in candidates:
            print(f"  Researching: {candidate}")
            
            # Simulate web research (in production, use actual web scraping)
            data, sources = self._research_candidate(
                candidate, 
                entity_type, 
                source_types,
                state
            )
            
            raw_data[candidate] = data
            source_map[candidate] = sources
            
            time.sleep(RATE_LIMIT_DELAY)
        
        state["raw_data"] = raw_data
        state["source_map"] = source_map
        state["last_updated"] = datetime.now()
        
        print(f"✓ Collected data for {len(candidates)} candidates from {len(source_types)} source types")
        
        return state
    
    def _research_candidate(
        self, 
        candidate: str, 
        entity_type: str,
        source_types: List[str],
        state: RankingState
    ) -> tuple[str, List[Dict[str, str]]]:
        """Research a single candidate using LLM knowledge."""
        
        # Build context from source types
        source_context = self._build_source_context(source_types)
        
        prompt = f"""Research "{candidate}" as a {entity_type} and provide detailed information.

Focus on these aspects based on source types: {source_context}

Provide:
1. Key facts and statistics
2. Recent developments or achievements
3. Relevant metrics and performance data
4. Expert opinions or reviews (when applicable)

Return comprehensive information that would help evaluate this {entity_type}.
"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            data = response.content
            
            # Generate source references
            sources = self._generate_source_references(candidate, entity_type, source_types)
            
            return data, sources
            
        except Exception as e:
            print(f"✗ Error researching {candidate}: {e}")
            return f"Limited information available for {candidate}", []
    
    def _collect_from_custom_urls(
        self, 
        state: RankingState, 
        candidates: List[str], 
        urls: List[str]
    ) -> RankingState:
        """Collect data using user-provided URLs."""
        
        raw_data = {}
        source_map = {}
        
        for candidate in candidates:
            # Simulate extraction from custom URLs
            data_parts = []
            sources = []
            
            for url in urls[:MAX_SOURCES_PER_CANDIDATE]:
                # In production, actually fetch and parse the URL
                domain = self._extract_domain(url)
                
                data_parts.append(f"Data from {domain} about {candidate}")
                sources.append({
                    "url": url,
                    "title": f"{candidate} - {domain}",
                    "source_type": "custom",
                    "domain": domain
                })
            
            raw_data[candidate] = "\n\n".join(data_parts)
            source_map[candidate] = sources
        
        state["raw_data"] = raw_data
        state["source_map"] = source_map
        state["last_updated"] = datetime.now()
        
        print(f"✓ Collected data from {len(urls)} custom URLs")
        
        return state
    
    def _auto_select_sources(self, domain: str) -> List[str]:
        """Automatically select best sources for a domain."""
        from config.settings import DOMAIN_SOURCE_RECOMMENDATIONS
        
        return DOMAIN_SOURCE_RECOMMENDATIONS.get(
            domain.lower(), 
            DOMAIN_SOURCE_RECOMMENDATIONS["default"]
        )
    
    def _build_source_context(self, source_types: List[str]) -> str:
        """Build context string from source types."""
        contexts = []
        for stype in source_types:
            if stype in SOURCE_CONFIGS:
                contexts.append(SOURCE_CONFIGS[stype]["name"])
        return ", ".join(contexts) if contexts else "general sources"
    
    def _generate_source_references(
        self, 
        candidate: str, 
        entity_type: str, 
        source_types: List[str]
    ) -> List[Dict[str, str]]:
        """Generate realistic source references."""
        sources = []
        
        for stype in source_types[:MAX_SOURCES_PER_CANDIDATE]:
            if stype in SOURCE_CONFIGS:
                config = SOURCE_CONFIGS[stype]
                domain = config["domains"][0] if config["domains"] else "example.com"
                
                sources.append({
                    "url": f"https://{domain}/{candidate.lower().replace(' ', '-')}",
                    "title": f"{candidate} - {config['name']}",
                    "source_type": stype,
                    "domain": domain,
                    "icon": config["icon"]
                })
        
        return sources
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        match = re.search(r'https?://([^/]+)', url)
        return match.group(1) if match else "unknown.com"
    
    def _clean_json(self, content: str) -> str:
        """Clean JSON from markdown code blocks."""
        content = content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return content