import json
from services.candidate_scorer import CandidateScorer

def test_candidate_scorer():
    print("="*50)
    print("TEST: CANDIDATE SCORING ENGINE (STRICT RUBRIC)")
    print("="*50)

    scorer = CandidateScorer()
    
    # -----------------------------------------------------
    # Mock Data: Simulating outputs from earlier pipeline steps
    # -----------------------------------------------------
    mock_semantic_strong = {
        "overall_similarity": 0.85,
        "skills_similarity": 0.95,  # (0.95^2.5)*10 = 8.7 -> 9
        "experience_similarity": 0.90 # (0.90^2.5)*10 = 7.6 -> 8
    }
    
    mock_resume_strong = """
    John Doe
    B.Tech CS from University of Tech. AWS Certified.
    - 5 years experience building scalable APIs.
    - Deployed microservices on AWS using Docker and Kubernetes.
    - Optimized database architecture for a production system.
    - See my github.com/johndoe for more.
    """ * 3
    
    mock_jd_data = {"education_requirements": ["Bachelor's degree"]}
    
    print("\n[+] Scoring Strong Professional Candidate...")
    result_strong = scorer.score_candidate(
        semantic_results=mock_semantic_strong,
        resume_full_text=mock_resume_strong,
        jd_data=mock_jd_data
    )
    
    print("\n--- STRONG CANDIDATE OUTPUT ---")
    print(json.dumps(result_strong, indent=2))
    
    assert result_strong["recommendation"] in ["Hire", "Consider"], "Strong candidate scored too low!"
    
    # -----------------------------------------------------
    # Test 2: Weak Beginner Candidate
    # -----------------------------------------------------
    mock_semantic_weak = {
        "overall_similarity": 0.60,
        "skills_similarity": 0.60,  # Strict scaling drops this drastically: (0.60^2.5)*10 = ~2.7 -> 3
        "experience_similarity": 0.50 # -> 1.7 -> 2
    }
    mock_resume_weak = """
    I am learning python. I am a ninja guru.
    Currently exploring AI and making a calculator tutorial.
    I have a B.A. in History.
    """
    
    print("\n[+] Scoring Weak Beginner Candidate...")
    result_weak = scorer.score_candidate(
        semantic_results=mock_semantic_weak,
        resume_full_text=mock_resume_weak,
        jd_data=mock_jd_data
    )
    
    print("\n--- WEAK CANDIDATE OUTPUT ---")
    print(json.dumps(result_weak, indent=2))
    
    assert result_weak["recommendation"] == "No Hire", "Weak candidate was over-scored!"
    assert result_weak["weighted_total"] < 5.0, "Weak candidate score inflation detected!"

    print("\n✅ Strict Candidate Scorer is actively preventing score inflation!")

if __name__ == "__main__":
    test_candidate_scorer()
