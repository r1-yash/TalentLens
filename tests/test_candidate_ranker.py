import json
from services.candidate_ranker import CandidateRanker

def test_candidate_ranker():
    print("="*50)
    print("TEST: CANDIDATE RANKING SYSTEM")
    print("="*50)

    ranker = CandidateRanker()

    # -----------------------------------------------------
    # Mock Data: Simulating the output list from CandidateScorer
    # -----------------------------------------------------
    mock_candidates = [
        {
            "candidate_name": "Bob Smith",
            "weighted_total": 4.25,
            "recommendation": "No Hire",
            "skills_match": {"score": 4},
            "experience_relevance": {"score": 5},
            "education_certs": {"score": 3},
            "project_portfolio": {"score": 4},
            "communication_quality": {"score": 5}
        },
        {
            "candidate_name": "Alice Johnson",
            "weighted_total": 8.95,
            "recommendation": "Hire",
            "skills_match": {"score": 9},
            "experience_relevance": {"score": 9},
            "education_certs": {"score": 8},
            "project_portfolio": {"score": 9},
            "communication_quality": {"score": 9}
        },
        {
            "candidate_name": "Charlie Brown",
            "weighted_total": 6.50,
            "recommendation": "Consider",
            "skills_match": {"score": 6},
            "experience_relevance": {"score": 7},
            "education_certs": {"score": 8},
            "project_portfolio": {"score": 5},
            "communication_quality": {"score": 6}
        }
    ]

    print(f"\n[+] Processing {len(mock_candidates)} mock candidates...")
    ranked_results = ranker.rank_candidates(mock_candidates)
    
    print("\n--- FINAL RANKED OUTPUT ---")
    print(json.dumps(ranked_results, indent=2))
    
    # -----------------------------------------------------
    # Validation Logic
    # -----------------------------------------------------
    assert ranked_results["top_candidate"]["candidate_name"] == "Alice Johnson", "Sorting logic failed!"
    assert ranked_results["ranked_candidates"][0]["rank"] == 1, "Ranks are incorrect"
    assert ranked_results["summary"]["Top Tier"] == 1, "Categorization logic failed"
    assert ranked_results["summary"]["Consider"] == 1, "Categorization logic failed"
    assert ranked_results["summary"]["Weak Match"] == 1, "Categorization logic failed"
    
    print("\n✅ Candidate Ranker successfully sorted and categorized all candidates!")

if __name__ == "__main__":
    test_candidate_ranker()
