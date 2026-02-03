"""Scoring Agent - Scores candidates and detects ranking changes."""

from typing import Dict, List, Optional
import json
import pandas as pd
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from config.state import RankingState
from config.settings import CHANGE_DETECTION_THRESHOLD

class ScoringAgent:
    """Agent responsible for scoring candidates and generating rankings."""
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        
    def score_candidates(self, state: RankingState) -> RankingState:
        """Score each candidate on each metric using collected data."""
        candidates = state.get("candidates", [])
        metrics = state.get("metrics", [])
        raw_data = state.get("raw_data", {})
        entity_type = state.get("entity_type", "items")
        
        if not candidates or not metrics:
            state["errors"] = state.get("errors", []) + ["Missing candidates or metrics"]
            return state
        
        scores = {}
        
        for candidate in candidates:
            candidate_data = raw_data.get(candidate, "")
            
            # Score this candidate on all metrics
            candidate_scores = self._score_single_candidate(
                candidate, 
                candidate_data,
                metrics,
                entity_type
            )
            
            scores[candidate] = candidate_scores
        
        state["scores"] = scores
        
        print(f"✓ Scored {len(candidates)} candidates on {len(metrics)} metrics")
        
        return state
    
    def generate_ranking(self, state: RankingState) -> RankingState:
        """Create a ranked table with total scores."""
        candidates = state.get("candidates", [])
        scores = state.get("scores", {})
        metrics = state.get("metrics", [])
        weights = state.get("weights", {})
        num_items = state.get("num_items", 10)
        
        if not scores:
            state["errors"] = state.get("errors", []) + ["No scores available"]
            return state
        
        # Build DataFrame
        rows = []
        for candidate in candidates:
            candidate_scores = scores.get(candidate, {})
            row = {"Name": candidate}
            
            for metric in metrics:
                row[metric] = candidate_scores.get(metric, 0.0)
            
            # Calculate weighted total
            total = sum(
                candidate_scores.get(m, 0.0) * weights.get(m, 0.0) 
                for m in metrics
            )
            row["Total Score"] = round(total, 3)
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df = df.sort_values("Total Score", ascending=False).reset_index(drop=True)
        
        # Store full dataframe
        state["full_table"] = df.copy()
        
        # Create display version with ranks
        df_display = df.head(num_items).copy()
        df_display.index = df_display.index + 1
        df_display.insert(0, "Rank", df_display.index)
        
        state["final_table"] = df_display
        state["total_available"] = len(df)
        
        print(f"✓ Generated ranking table with {len(df)} candidates")
        
        return state
    
    def detect_changes(self, state: RankingState) -> RankingState:
        """Detect significant changes in rankings compared to previous state."""
        current_scores = state.get("scores", {})
        previous_scores = state.get("previous_scores", {})
        
        if not previous_scores:
            print("ℹ No previous scores for comparison")
            state["changes_detected"] = {}
            return state
        
        changes = {}
        
        for candidate, curr_scores in current_scores.items():
            if candidate not in previous_scores:
                # New candidate
                changes[candidate] = {
                    "type": "new",
                    "message": f"{candidate} is new to the ranking"
                }
                continue
            
            prev_scores = previous_scores[candidate]
            
            # Check each metric for significant changes
            metric_changes = {}
            for metric, curr_value in curr_scores.items():
                prev_value = prev_scores.get(metric, 0.0)
                diff = curr_value - prev_value
                
                if abs(diff) >= CHANGE_DETECTION_THRESHOLD:
                    metric_changes[metric] = {
                        "previous": prev_value,
                        "current": curr_value,
                        "change": diff,
                        "percent_change": (diff / prev_value * 100) if prev_value > 0 else 0
                    }
            
            if metric_changes:
                changes[candidate] = {
                    "type": "updated",
                    "metrics": metric_changes,
                    "message": self._generate_change_message(candidate, metric_changes)
                }
        
        # Check for removed candidates
        for candidate in previous_scores:
            if candidate not in current_scores:
                changes[candidate] = {
                    "type": "removed",
                    "message": f"{candidate} is no longer in the ranking"
                }
        
        state["changes_detected"] = changes
        
        if changes:
            print(f"⚠ Detected changes in {len(changes)} candidates")
        else:
            print("✓ No significant changes detected")
        
        return state
    
    def _score_single_candidate(
        self,
        candidate: str,
        candidate_data: str,
        metrics: List[str],
        entity_type: str
    ) -> Dict[str, float]:
        """Score a single candidate on all metrics."""
        
        prompt = f"""Score "{candidate}" (a {entity_type}) on these metrics: {', '.join(metrics)}

Available information:
{candidate_data[:2000]}  # Truncate to avoid token limits

For each metric, provide a score between 0.0 and 1.0 where:
- 1.0 = Exceptional/Best in class
- 0.7-0.9 = Very good
- 0.5-0.7 = Good/Average
- 0.3-0.5 = Below average
- 0.0-0.3 = Poor

Return ONLY a JSON object mapping metric names to scores.
Example: {{"metric1": 0.85, "metric2": 0.72, "metric3": 0.91}}
"""
        
        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            content = self._clean_json(response.content)
            
            scores = json.loads(content)
            
            # Ensure all metrics have scores
            for metric in metrics:
                if metric not in scores:
                    scores[metric] = 0.5  # Default to middle score
            
            return scores
            
        except Exception as e:
            print(f"✗ Error scoring {candidate}: {e}")
            # Return default scores
            return {m: 0.5 for m in metrics}
    
    def _generate_change_message(
        self, 
        candidate: str, 
        metric_changes: Dict[str, Dict]
    ) -> str:
        """Generate a human-readable message about metric changes."""
        messages = []
        
        for metric, change_data in metric_changes.items():
            change = change_data["change"]
            direction = "increased" if change > 0 else "decreased"
            percent = abs(change_data["percent_change"])
            
            metric_display = metric.replace("_", " ").title()
            messages.append(
                f"{metric_display} {direction} by {percent:.1f}% "
                f"({change_data['previous']:.2f} → {change_data['current']:.2f})"
            )
        
        return f"{candidate}: " + "; ".join(messages)
    
    def generate_change_summary(self, state: RankingState) -> Optional[str]:
        """Generate a user-friendly summary of detected changes."""
        changes = state.get("changes_detected", {})
        
        if not changes:
            return None
        
        summary_parts = ["📊 **Ranking Updates Detected:**\n"]
        
        new_entries = [c for c, d in changes.items() if d["type"] == "new"]
        updated_entries = [c for c, d in changes.items() if d["type"] == "updated"]
        removed_entries = [c for c, d in changes.items() if d["type"] == "removed"]
        
        if new_entries:
            summary_parts.append(f"✨ **New:** {', '.join(new_entries[:3])}")
            if len(new_entries) > 3:
                summary_parts[-1] += f" (+{len(new_entries) - 3} more)"
        
        if updated_entries:
            summary_parts.append(f"\n📈 **Updated:** {len(updated_entries)} candidates with metric changes")
            # Show top 2 most significant changes
            for candidate in updated_entries[:2]:
                summary_parts.append(f"  • {changes[candidate]['message']}")
        
        if removed_entries:
            summary_parts.append(f"\n❌ **Removed:** {', '.join(removed_entries)}")
        
        summary_parts.append(f"\n\n_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
        
        return "\n".join(summary_parts)
    
    def _clean_json(self, content: str) -> str:
        """Clean JSON from markdown code blocks."""
        content = content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return content