import json
from services.candidate_scorer import CandidateScorer

def test_candidate_scorer():
    print("="*50)
    print("TEST: CANDIDATE SCORING ENGINE (RUBRIC)")
    print("="*50)

    scorer = CandidateScorer()
    
    # -----------------------------------------------------
    # Mock Data: Simulating outputs from earlier pipeline steps
    # -----------------------------------------------------
    mock_semantic_strong = {
        "overall_similarity": 0.85,
        "skills_similarity": 0.92,  # Should normalize to ~9
        "experience_similarity": 0.88 # Should normalize to ~9
    }
    
    mock_resume_strong = """
    John Doe
    Bachelor of Science in Computer Science from University of Tech.
    Experience: 5 years building scalable APIs.
    Projects: See my github.com/johndoe for machine learning apps deployed on AWS.
    I am a highly motivated engineer.
    """ * 10 # Multiplying to simulate a normal length resume for communication heuristics
    
    mock_jd_data = {"education_requirements": ["Bachelor's degree"]}
    
    # -----------------------------------------------------
    # Test 1: Strong Candidate
    # -----------------------------------------------------
    print("\n[+] Scoring Strong Candidate...")
    result_strong = scorer.score_candidate(
        semantic_results=mock_semantic_strong,
        resume_full_text=mock_resume_strong,
        jd_data=mock_jd_data
    )
    
    print("\n--- STRONG CANDIDATE OUTPUT ---")
    print(json.dumps(result_strong, indent=2))
    
    assert result_strong["recommendation"] == "Hire", "Strong candidate should be a Hire!"
    assert result_strong["weighted_total"] >= 7.5, "Strong candidate score too low!"
    
    # -----------------------------------------------------
    # Test 2: Weak Candidate
    # -----------------------------------------------------
    mock_semantic_weak = {
        "overall_similarity": 0.20,
        "skills_similarity": 0.30,  # Should normalize to 3
        "experience_similarity": 0.15 # Should normalize to 1 or 2
    }
    mock_resume_weak = "I am a guy. I like computers." # Very short, no keywords
    
    print("\n[+] Scoring Weak Candidate...")
    result_weak = scorer.score_candidate(
        semantic_results=mock_semantic_weak,
        resume_full_text=mock_resume_weak,
        jd_data=mock_jd_data
    )
    
    print("\n--- WEAK CANDIDATE OUTPUT ---")
    print(json.dumps(result_weak, indent=2))
    
    assert result_weak["recommendation"] == "No Hire", "Weak candidate should be a No Hire!"
    assert result_weak["weighted_total"] < 5.0, "Weak candidate score too high!"

    print("\n✅ Candidate Scorer strictly follows the internship rubric and weighting!")

if __name__ == "__main__":
    test_candidate_scorer()
