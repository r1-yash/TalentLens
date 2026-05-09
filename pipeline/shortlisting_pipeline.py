import time
from typing import List, Dict, Any, Tuple
from core.logger import get_logger
from agents.jd_parser_agent import JDParsingAgent
from services.semantic_matcher import SemanticMatcher
from services.candidate_scorer import CandidateScorer
from services.candidate_ranker import CandidateRanker
from utils.document_parser import extract_text_from_pdf, extract_text_from_docx

logger = get_logger(__name__)

class ShortlistingPipeline:
    """
    Central Orchestrator that connects the Parsers, Agents, and Services together.
    """
    def __init__(self):
        logger.info("Initializing Shortlisting Pipeline Orchestrator...")
        self.jd_agent = JDParsingAgent()
        self.matcher = SemanticMatcher()
        self.scorer = CandidateScorer()
        self.ranker = CandidateRanker()

    def _extract_text(self, file_name: str, file_stream) -> str:
        """Helper to extract text based on extension."""
        ext = file_name.lower().split('.')[-1]
        try:
            if ext == 'pdf':
                return extract_text_from_pdf(file_stream)
            elif ext == 'docx':
                return extract_text_from_docx(file_stream)
            elif ext == 'txt':
                return file_stream.read().decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting {file_name}: {e}")
        return ""

    def process_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Parses the raw JD into structured Pydantic data."""
        parsed_jd = self.jd_agent.parse_jd(jd_text)
        if not parsed_jd:
            raise ValueError("JD Parsing Agent failed to return structured data.")
        return parsed_jd.model_dump()

    def process_candidates(self, jd_data: Dict[str, Any], jd_raw_text: str, resumes: List[Tuple[str, Any]]) -> Dict[str, Any]:
        """
        Orchestrates processing multiple resumes against a parsed JD.
        resumes: List of tuples (file_name, file_stream)
        """
        logger.info(f"Processing {len(resumes)} resumes through the pipeline...")
        scored_candidates = []

        # Prepare JD semantic strings
        jd_skills_str = " ".join(jd_data.get("required_skills", []) + jd_data.get("preferred_skills", []))
        jd_exp_str = str(jd_data.get("minimum_experience", 0)) + " years experience. " + " ".join(jd_data.get("responsibilities", []))

        for filename, file_stream in resumes:
            logger.info(f"Analyzing {filename}...")
            resume_text = self._extract_text(filename, file_stream)
            
            if not resume_text.strip():
                logger.warning(f"Could not extract text from {filename}. Skipping.")
                continue

            # Step 1: Semantic Match
            match_results = self.matcher.match_candidate(
                jd_full_text=jd_raw_text,
                jd_skills=jd_skills_str,
                jd_experience=jd_exp_str,
                resume_full_text=resume_text,
                resume_skills=resume_text,  # proxy until specific section parser is added
                resume_experience=resume_text # proxy until specific section parser is added
            )

            # Step 2: Score Candidate (Rubric)
            candidate_score = self.scorer.score_candidate(
                semantic_results=match_results,
                resume_full_text=resume_text,
                jd_data=jd_data
            )
            
            # Clean filename to use as candidate name fallback
            clean_name = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
            candidate_score["candidate_name"] = clean_name
            scored_candidates.append(candidate_score)

        # Step 3: Rank and Categorize
        final_results = self.ranker.rank_candidates(scored_candidates)
        return final_results
