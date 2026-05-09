import re
from typing import Dict, Any
from core.logger import get_logger

logger = get_logger(__name__)

class CandidateScorer:
    """
    Candidate Scoring Engine that evaluates resumes against the mandatory internship rubric.
    Uses deterministic scoring based on semantic similarities and heuristic text analysis.
    """
    
    # Mandatory Evaluation Weights from the Internship PDF
    WEIGHTS = {
        "skills_match": 0.30,
        "experience_relevance": 0.25,
        "education_certs": 0.15,
        "project_portfolio": 0.20,
        "communication_quality": 0.10
    }
    
    def __init__(self):
        logger.info("Initializing CandidateScoring Engine...")

    def _normalize_score(self, raw_value: float, max_expected: float = 1.0) -> int:
        """Converts a raw metric (like cosine similarity) into a 0-10 score safely."""
        score = int(round((raw_value / max_expected) * 10))
        return max(0, min(10, score))

    def score_skills_match(self, skills_similarity: float) -> Dict[str, Any]:
        """Weight: 30%. Driven by Semantic Matcher output."""
        score = self._normalize_score(skills_similarity)
        if score >= 8:
            justification = "Strong alignment with required technical and preferred skills (>80% match)."
        elif score >= 5:
            justification = "Moderate skills match; possesses core requirements but lacks some preferred skills."
        else:
            justification = "Poor skills match; missing critical technical requirements."
        return {"score": score, "justification": justification}

    def score_experience_relevance(self, experience_similarity: float) -> Dict[str, Any]:
        """Weight: 25%. Driven by Semantic Matcher output."""
        score = self._normalize_score(experience_similarity)
        if score >= 8:
            justification = "Experience is highly relevant to the JD's domain and seniority expectations."
        elif score >= 5:
            justification = "Adjacent domain experience; meets minimum years but lacks exact domain match."
        else:
            justification = "Experience is unrelated or does not meet the minimum required years."
        return {"score": score, "justification": justification}

    def score_education_certs(self, resume_text: str, jd_education: list) -> Dict[str, Any]:
        """Weight: 15%. Deterministic keyword heuristic."""
        text_lower = resume_text.lower()
        has_degree = any(keyword in text_lower for keyword in ["bachelor", "master", "phd", "b.s", "b.a", "degree", "university", "college", "certification"])
        
        if has_degree:
            score = 8
            justification = "Meets foundational educational requirements (degree/certification detected)."
        else:
            score = 3
            justification = "Does not clearly mention required degrees or certifications."
            
        return {"score": score, "justification": justification}

    def score_project_portfolio(self, resume_text: str) -> Dict[str, Any]:
        """Weight: 20%. Deterministic check for links and project evidence."""
        text_lower = resume_text.lower()
        has_portfolio = any(keyword in text_lower for keyword in ["github.com", "portfolio", "projects", "deployed", "live at", "kaggle.com"])
        
        if has_portfolio:
            score = 9
            justification = "Strong evidence of practical projects and portfolio links provided."
        else:
            score = 4
            justification = "Generic or missing evidence of personal/professional project portfolio."
            
        return {"score": score, "justification": justification}

    def score_communication_quality(self, resume_text: str) -> Dict[str, Any]:
        """Weight: 10%. Evaluates structural length and detail as a baseline proxy."""
        length = len(resume_text.split())
        if length > 250:
            score = 8
            justification = "Resume is well-structured with adequate detail and clear formatting."
        elif length > 100:
            score = 6
            justification = "Adequate clarity but lacks in-depth descriptions."
        else:
            score = 3
            justification = "Resume lacks detail or structure, suggesting poor communication of experience."
            
        return {"score": score, "justification": justification}

    def calculate_weighted_total(self, scores: Dict[str, int]) -> float:
        """Applies exact weights from the rubric to calculate final score."""
        total = 0.0
        for dim, weight in self.WEIGHTS.items():
            total += scores[dim] * weight
        return round(total, 2)

    def generate_recommendation(self, total_score: float) -> str:
        """Maps weighted score to final decision."""
        if total_score >= 7.5:
            return "Hire"
        elif total_score >= 5.0:
            return "Consider"
        else:
            return "No Hire"

    def score_candidate(self, 
                        semantic_results: Dict[str, float], 
                        resume_full_text: str,
                        jd_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entrypoint. Takes semantic scores and raw text data to build the final rubric.
        """
        logger.info("Computing rubric scores for candidate...")
        jd_data = jd_data or {}
        
        # 1. Compute Individual Dimensions
        skills = self.score_skills_match(semantic_results.get("skills_similarity", 0.0))
        experience = self.score_experience_relevance(semantic_results.get("experience_similarity", 0.0))
        education = self.score_education_certs(resume_full_text, jd_data.get("education_requirements", []))
        portfolio = self.score_project_portfolio(resume_full_text)
        communication = self.score_communication_quality(resume_full_text)

        # 2. Aggregate
        dimension_scores = {
            "skills_match": skills["score"],
            "experience_relevance": experience["score"],
            "education_certs": education["score"],
            "project_portfolio": portfolio["score"],
            "communication_quality": communication["score"]
        }
        
        weighted_total = self.calculate_weighted_total(dimension_scores)
        recommendation = self.generate_recommendation(weighted_total)

        final_output = {
            "skills_match": skills,
            "experience_relevance": experience,
            "education_certs": education,
            "project_portfolio": portfolio,
            "communication_quality": communication,
            "weighted_total": weighted_total,
            "recommendation": recommendation
        }
        
        logger.info(f"Candidate scored: {weighted_total}/10 -> {recommendation}")
        return final_output
