import re
import requests
from typing import Dict, Any, List
from core.logger import get_logger
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI

logger = get_logger(__name__)

class CandidateScorer:
    """
    Candidate Scoring Engine that evaluates resumes against the mandatory internship rubric.
    Uses smarter, strict deterministic heuristics to avoid score inflation for weak resumes.
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
        logger.info("Initializing Strict CandidateScoring Engine...")
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.model_name,
                google_api_key=settings.google_api_key,
                temperature=0.0
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM for scorer: {e}")
            self.llm = None

    def score_skills_match(self, skills_similarity: float, resume_text: str = "", jd_required_skills: List[str] = None) -> Dict[str, Any]:
        """Weight: 30%. Driven primarily by direct stack overlap, adjusted by semantic similarity."""
        if jd_required_skills is None:
            jd_required_skills = []
            
        text_lower = resume_text.lower()
        
        # Calculate stack overlap
        matched = 0
        total = len(jd_required_skills)
        for skill in jd_required_skills:
            if skill.lower() in text_lower:
                matched += 1
        
        match_pct = matched / total if total > 0 else 1.0
        
        # Primary base score driven by stack match
        if match_pct > 0.75:
            base_score = 8
            justification = f"Excellent stack match ({int(match_pct*100)}%)."
        elif match_pct >= 0.60:
            base_score = 6
            justification = f"Good stack match ({int(match_pct*100)}%)."
        elif match_pct >= 0.50:
            base_score = 5
            justification = f"Moderate stack match ({int(match_pct*100)}%)."
        elif match_pct >= 0.30:
            base_score = 3
            justification = f"Partial stack match ({int(match_pct*100)}%)."
        else:
            base_score = 2
            justification = f"Significant stack mismatch ({int(match_pct*100)}%)."
            
        # Semantic adjustment (+/- 1 or 2)
        semantic_adj = 0
        if skills_similarity >= 0.65:
            semantic_adj = 2
        elif skills_similarity >= 0.50:
            semantic_adj = 1
        elif skills_similarity < 0.25:
            semantic_adj = -1
            
        score = base_score + semantic_adj
        
        # Floor logic
        if match_pct > 0.40:
            score = max(4, score)
            
        # Keyword bonus for modern AI/ML stack
        modern_ai_stack = ["langchain", "rag", "fastapi", "llm", "mlops", "langgraph", "pydantic", "embeddings", "vector", "aws", "ci/cd", "docker", "pytorch", "huggingface", "transformers", "langsmith"]
        bonus_points = sum(1 for kw in modern_ai_stack if kw in text_lower)
        if bonus_points >= 3:
            score += 2
        elif bonus_points >= 1:
            score += 1
            
        score = max(1, min(10, score))
        
        if score >= 8:
            justification = "Strong skills alignment with required technologies. " + justification
        elif score >= 5:
            justification = "Moderate skills match; covers basics but lacks depth. " + justification
        else:
            justification = "Poor skills match; missing critical required technologies. " + justification
            
        return {"score": score, "justification": justification.strip()}

    def score_experience_relevance(self, experience_similarity: float, resume_full_text: str = "", jd_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Weight: 25%. Experience hierarchy (FT vs Intern) + Domain Match Matrix."""
        if jd_data is None:
            jd_data = {}
            
        text_lower = resume_full_text.lower()
        
        # Extract JD terms
        jd_title = jd_data.get("role_title", "").lower()
        jd_skills = jd_data.get("required_skills", [])
        jd_terms = set(jd_skills + jd_title.split())
        jd_terms = {t.lower() for t in jd_terms if len(t) > 2}
        
        # 1. Detect Domain Match
        matched_terms = sum(1 for term in jd_terms if term in text_lower)
        domain_match_pct = (matched_terms / len(jd_terms)) if len(jd_terms) > 0 else 1.0
        
        if domain_match_pct >= 0.60:
            domain_level = "Exact"
        elif domain_match_pct >= 0.30:
            domain_level = "Adjacent"
        else:
            domain_level = "Unrelated"
            
        # 2. Detect Experience Type & Duration
        intern_signals = any(kw in text_lower for kw in ["intern", "internship", "trainee", "apprentice"])
        fulltime_signals = any(kw in text_lower for kw in ["full-time", "fulltime", "senior", "lead", "manager", "engineer at", "developer at"])
        
        # Extract year spans using regex
        year_matches = re.findall(r'(20\d{2})\s*[-–]\s*(20\d{2}|present|current)', text_lower)
        max_duration = 0
        for start, end in year_matches:
            try:
                start_yr = int(start)
                end_yr = 2024 if end in ['present', 'current'] else int(end)
                duration = end_yr - start_yr
                if duration > max_duration:
                    max_duration = duration
            except ValueError:
                continue
                
        # Classify Experience Type
        exp_type = "No experience"
        if fulltime_signals or max_duration >= 1:
            if max_duration >= 3 or any(kw in text_lower for kw in ["senior", "lead", "manager", "5+ years", "4+ years"]):
                exp_type = "Full-time 3+ years"
            else:
                exp_type = "Full-time 1-2 years"
        elif intern_signals:
            exp_type = "Internship"
        elif any(kw in text_lower for kw in ["experience", "worked at"]):
            # Fallback if vague
            exp_type = "Internship"
            
        # 3. Final Score Matrix & Semantic Adjustment
        # Semantic gives a slight bump within the band
        bump = 1 if experience_similarity >= 0.55 else 0
        
        if exp_type == "Full-time 3+ years":
            if domain_level == "Exact":
                score = 9 + bump
            elif domain_level == "Adjacent":
                score = 7 + bump
            else:
                score = 4 + bump
        elif exp_type == "Full-time 1-2 years":
            if domain_level == "Exact":
                score = 7 + bump
            elif domain_level == "Adjacent":
                score = 6 + bump
            else:
                score = 3 + bump
        elif exp_type == "Internship":
            if domain_level == "Exact":
                score = 6 + bump
            elif domain_level == "Adjacent":
                score = 4 + bump
            else:
                score = 2 + bump
        else: # No experience
            if domain_level == "Exact" or domain_level == "Adjacent":
                score = 1 + bump
            else:
                score = 1

        score = min(10, max(1, score))
        
        # 4. Generate Justification
        if exp_type == "No experience":
            justification = "No professional work experience detected. Pure academic profile."
        else:
            justification = f"{exp_type} experience with {domain_level.lower()} domain alignment to JD requirements."

        return {"score": score, "justification": justification}

    def score_education_certs(self, resume_text: str, jd_education: list) -> Dict[str, Any]:
        """Weight: 15%. Strict hierarchical education evaluation matching JD."""
        text_lower = resume_text.lower()
        score = 3
        justification = ""
        
        jd_edu_str = " ".join(jd_education).lower() if jd_education else ""
        requires_masters = any(kw in jd_edu_str for kw in ["master", "ms", "mtech"])
        requires_bachelors = any(kw in jd_edu_str for kw in ["bachelor", "btech", "be", "b.e", "b.tech", "degree"])
        
        has_masters = any(kw in text_lower for kw in ["mtech", "m.tech", "ms cs", "master"])
        has_btech_cs = any(kw in text_lower for kw in ["btech cs", "b.tech cs", "btech computer", "b.tech in computer", "ai/ml", "artificial intelligence"])
        has_btech = any(kw in text_lower for kw in ["btech", "b.tech", "bachelor of technology", "b.e.", "bachelor of engineering"])
        has_bsc = any(kw in text_lower for kw in ["bca", "bsc cs", "b.sc", "bachelor of science"])
        has_degree = has_masters or has_btech or has_bsc or "bachelor" in text_lower or "degree" in text_lower
        
        if requires_masters:
            if has_masters:
                score = 9
                justification = "Meets Masters degree requirement."
            elif has_btech:
                score = 6
                justification = "Holds Bachelors, but Masters preferred."
            elif has_bsc:
                score = 3
                justification = "Holds basic degree; falls short of Masters requirement."
            else:
                score = 2
                justification = "Does not meet educational requirements."
        elif requires_bachelors or not jd_education:
            if has_btech_cs or has_masters:
                score = 9
                justification = "Holds a highly relevant Tier-1 degree (CS/AI)."
            elif has_btech:
                score = 7
                justification = "Holds an engineering degree."
            elif has_bsc:
                score = 5
                justification = "Holds a foundational technical degree (BCA/BSc)."
            elif not has_degree:
                score = 2
                justification = "No relevant technical degree detected."
            else:
                score = 4
                justification = "Holds an unrelated degree."
                
        has_certs = any(kw in text_lower for kw in ["aws certified", "google cloud", "tensorflow", "coursera", "udemy", "certification", "certified"])
        if has_certs:
            score = min(10, score + 1)
            justification += " (Includes relevant technical certifications)."
            
        return {"score": score, "justification": justification}

    def score_project_portfolio(self, resume_text: str, jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """Weight: 20%. Multi-tiered grading based on real projects, Github links, and deployments."""
        jd_required_skills = jd_data.get("required_skills", [])
        jd_title = jd_data.get("role_title", "").lower()
        
        text_lower = resume_text.lower()
        
        # Extract GitHub URLs
        github_urls = set(re.findall(r'github\.com/[\w-]+/[\w-]+', text_lower))
        valid_repos = 0
        for url in github_urls:
            full_url = f"https://{url}" if not url.startswith("http") else url
            try:
                resp = requests.head(full_url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
                if resp.status_code == 200:
                    valid_repos += 1
            except requests.RequestException:
                pass

        # Identify completed / deployed projects heuristically
        deploy_kws = ["deployed", "live at", "production", "hosted on", "vercel", "heroku", "aws", "gcp", "launched", "api"]
        build_kws = ["built", "developed", "created", "architected", "designed"]
        
        deployed_signals = sum(1 for kw in deploy_kws if kw in text_lower)
        completed_signals = sum(1 for kw in build_kws if kw in text_lower)
        
        strong_completed_projects = 0
        if deployed_signals >= 2 and completed_signals >= 2:
            strong_completed_projects = 2
        elif deployed_signals >= 1 or completed_signals >= 1:
            strong_completed_projects = 1
            
        # Relevance to JD Stack
        relevant_tech_matches = sum(1 for skill in jd_required_skills if skill.lower() in text_lower)
        has_strong_jd_relevance = len(jd_required_skills) > 0 and (relevant_tech_matches / len(jd_required_skills)) >= 0.5
        has_partial_jd_relevance = len(jd_required_skills) > 0 and relevant_tech_matches >= 1
        
        # Adjacent domain check
        is_ai_domain = any(kw in jd_title for kw in ["ai", "ml", "machine learning", "data", "llm", "research"])
        has_ai_projects = any(kw in text_lower for kw in ["machine learning", "model", "dataset", "training", "pytorch", "tensorflow", "llm", "rag", "langchain"])
        adjacent_domain_match = (is_ai_domain and has_ai_projects) or (not is_ai_domain and not has_ai_projects)
        
        # Beginner flags
        beginner_flags = any(kw in text_lower for kw in ["learning", "exploring", "in progress", "tutorial", "academic project"])

        score = 3
        justification = ""
        
        if strong_completed_projects >= 2 and has_strong_jd_relevance and deployed_signals > 0:
            score = 9
            justification = "Multiple strong, deployed projects directly matching JD tech stack."
        elif strong_completed_projects >= 1 and has_partial_jd_relevance and deployed_signals > 0:
            score = 7
            justification = "Deployed project(s) with partial overlap to JD stack."
        elif strong_completed_projects >= 1 and adjacent_domain_match and deployed_signals > 0:
            score = 6
            justification = "Deployed project(s) in a relevant adjacent domain."
        elif strong_completed_projects >= 1 and deployed_signals > 0:
            score = 5
            justification = "Completed deployed project(s) but lacking clear JD relevance."
        elif strong_completed_projects > 0:
            score = 4
            justification = "Completed project(s) present but lack deployment evidence."
        elif valid_repos > 0:
            score = 4
            justification = "GitHub repositories present but unclear if projects are completed/deployed."
        elif beginner_flags:
            score = 2
            justification = "Only beginner, academic, or 'in-progress' projects found."
        else:
            score = 1
            justification = "No substantial projects found."
            
        # Github bonus
        if valid_repos > 0:
            score = min(10, score + 1)
            justification += " (Verified GitHub links present)."

        return {"score": score, "justification": justification.strip()}

    def score_communication_quality(self, resume_text: str) -> Dict[str, Any]:
        """Weight: 10%. Evaluates structural markers, action verbs, and quantification."""
        score = 8 # Start with a strong baseline and penalize
        text_lower = resume_text.lower()
        justification_flags = []
        
        # Soft skills listed as primary content (penalty)
        soft_skills = ["teamwork", "adaptability", "communication", "hard working", "leadership skills"]
        soft_skill_count = sum(1 for kw in soft_skills if kw in text_lower)
        if soft_skill_count >= 2:
            score -= 2
            justification_flags.append("Relies heavily on soft skill buzzwords.")
            
        # Quantified results (no numbers -> penalty)
        if not re.search(r'\d+', resume_text):
            score -= 1
            justification_flags.append("Lacks quantified results or metrics.")
            
        # Action verbs
        action_verbs = ["built", "developed", "deployed", "designed", "led", "architected", "improved", "managed", "created"]
        if not any(verb in text_lower for verb in action_verbs):
            score -= 2
            justification_flags.append("Missing strong action verbs.")
            
        # Word count check
        word_count = len(resume_text.split())
        if word_count < 200:
            score = min(score, 4)
            justification_flags.append("Resume is too brief (< 200 words).")
            
        score = max(1, min(10, score))
        
        if score >= 8:
            justification = "Professional communication: structured, quantified, and action-oriented."
        elif score >= 5:
            justification = "Adequate communication. " + " ".join(justification_flags)
        else:
            justification = "Poor communication. " + " ".join(justification_flags)
            
        return {"score": score, "justification": justification.strip()}

    def calculate_weighted_total(self, scores: Dict[str, int]) -> float:
        """Applies exact weights from the rubric to calculate final score."""
        total = 0.0
        for dim, weight in self.WEIGHTS.items():
            total += scores[dim] * weight
        return round(total, 2)

    def generate_recommendation(self, total_score: float) -> str:
        """Maps weighted score to final decision. Harsher thresholds for realism."""
        if total_score >= 7.5:
            return "Hire"
        elif total_score >= 5.5:
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
        logger.info("Computing STRICT rubric scores for candidate...")
        jd_data = jd_data or {}
        
        jd_required_skills = jd_data.get("required_skills", [])
        jd_experience = str(jd_data.get("minimum_experience", "")) + " " + " ".join(jd_data.get("responsibilities", []))
        
        skills = self.score_skills_match(semantic_results.get("skills_similarity", 0.0), resume_full_text, jd_required_skills)
        experience = self.score_experience_relevance(semantic_results.get("experience_similarity", 0.0), resume_full_text, jd_data)
        education = self.score_education_certs(resume_full_text, jd_data.get("education_requirements", []))
        portfolio = self.score_project_portfolio(resume_full_text, jd_data)
        communication = self.score_communication_quality(resume_full_text)

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
