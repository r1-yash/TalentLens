import os
import json
from dotenv import load_dotenv
load_dotenv(override=True)

from utils.document_parser import extract_text_from_pdf
from agents.jd_parser_agent import JDParsingAgent
from services.semantic_matcher import SemanticMatcher
from services.candidate_scorer import CandidateScorer

def run_e2e_test():
    print("="*50)
    print("🚀 END-TO-END PIPELINE TEST")
    print("="*50)
    
    # Your specific resume path you tested earlier!
    resume_path = "/Users/yashsinghal/Desktop/Yash_Resume_ML-2.pdf"
    
    # We will use the sample JD we created
    jd_path = "tests/sample_data/sample_jd.txt"
    
    if not os.path.exists(resume_path):
        print(f"❌ Could not find resume at {resume_path}")
        return
        
    print("\n[1] Extracting Texts...")
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_raw_text = f.read()
    
    resume_raw_text = extract_text_from_pdf(resume_path)
    if not resume_raw_text:
        print("❌ Failed to parse resume PDF.")
        return
    print("✅ Texts extracted successfully.")
    
    print("\n[2] Parsing JD with Gemini...")
    jd_agent = JDParsingAgent()
    jd_parsed = jd_agent.parse_jd(jd_raw_text)
    if not jd_parsed:
        print("❌ JD Parsing failed.")
        return
    print(f"✅ JD Parsed. Role: {jd_parsed.role_title}")
    
    print("\n[3] Running Semantic Matching...")
    matcher = SemanticMatcher()
    
    # We pass the full resume text for skills/experience since we haven't
    # built a specific Resume Section Parsing Agent yet.
    semantic_results = matcher.match_candidate(
        jd_full_text=jd_raw_text,
        jd_skills=jd_parsed.required_skills + jd_parsed.preferred_skills,
        jd_experience=str(jd_parsed.minimum_experience) + " years experience " + " ".join(jd_parsed.responsibilities),
        resume_full_text=resume_raw_text,
        resume_skills=resume_raw_text, 
        resume_experience=resume_raw_text 
    )
    print(f"✅ Semantic matching complete: {semantic_results}")
    
    print("\n[4] Running Candidate Scorer...")
    scorer = CandidateScorer()
    
    jd_dict = jd_parsed.model_dump()
    
    final_score = scorer.score_candidate(
        semantic_results=semantic_results,
        resume_full_text=resume_raw_text,
        jd_data=jd_dict
    )
    
    print("\n" + "="*50)
    print("FINAL CANDIDATE REPORT (YOUR RESUME)")
    print("="*50)
    print(json.dumps(final_score, indent=2))

if __name__ == "__main__":
    run_e2e_test()
