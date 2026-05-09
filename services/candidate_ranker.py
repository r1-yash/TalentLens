from typing import List, Dict, Any
from core.logger import get_logger

logger = get_logger(__name__)

class CandidateRanker:
    """
    Candidate Ranking System that sorts scored candidates, extracts key metrics,
    and groups them into shortlist tiers.
    """
    def __init__(self):
        logger.info("Initializing Candidate Ranking Engine...")

    def _categorize_candidate(self, score: float) -> str:
        """Determines the shortlist categorization based on the weighted total score."""
        if score >= 7.5:
            return "Top Tier"
        elif score >= 5.0:
            return "Consider"
        else:
            return "Weak Match"

    def rank_candidates(self, scored_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes a list of candidate dictionaries (from CandidateScorer)
        and returns a sorted, categorized shortlist payload.
        """
        if not scored_candidates:
            logger.warning("No candidates provided for ranking.")
            return {
                "ranked_candidates": [], 
                "top_candidate": None, 
                "summary": {"total_candidates": 0, "Top Tier": 0, "Consider": 0, "Weak Match": 0}
            }

        logger.info(f"Ranking {len(scored_candidates)} candidates...")
        
        # Sort candidates descending by weighted_total score
        sorted_candidates = sorted(
            scored_candidates, 
            key=lambda x: x.get("weighted_total", 0.0), 
            reverse=True
        )
        
        ranked_list = []
        summary = {
            "total_candidates": len(sorted_candidates),
            "Top Tier": 0,
            "Consider": 0,
            "Weak Match": 0
        }

        for idx, candidate in enumerate(sorted_candidates):
            score = candidate.get("weighted_total", 0.0)
            category = self._categorize_candidate(score)
            
            # Increment summary statistics
            summary[category] += 1
            
            # Build cleaned flat object for output and future UI presentation
            ranked_list.append({
                "rank": idx + 1,
                "candidate_name": candidate.get("candidate_name", "Unknown"),
                "weighted_total": score,
                "recommendation": candidate.get("recommendation", "No Hire"),
                "categorization": category,
                "rubric_scores": {
                    "skills_match": candidate.get("skills_match", {}).get("score", 0),
                    "experience_relevance": candidate.get("experience_relevance", {}).get("score", 0),
                    "education_certs": candidate.get("education_certs", {}).get("score", 0),
                    "project_portfolio": candidate.get("project_portfolio", {}).get("score", 0),
                    "communication_quality": candidate.get("communication_quality", {}).get("score", 0)
                }
            })

        top_candidate = ranked_list[0] if ranked_list else None

        output = {
            "ranked_candidates": ranked_list,
            "top_candidate": top_candidate,
            "summary": summary
        }
        
        logger.info("Ranking complete. Leaderboard generated.")
        return output
