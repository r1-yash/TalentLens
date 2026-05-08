from services.semantic_matcher import SemanticMatcher

def test_semantic_matcher():
    print("="*50)
    print("TEST: SEMANTIC MATCHING ENGINE")
    print("="*50)
    
    print("\n[+] Loading embedding model 'all-MiniLM-L6-v2'...")
    print("    (This may take 10-20 seconds on the very first run to download the model)")
    matcher = SemanticMatcher()
    
    # -------------------------------------
    # Dummy Data Setup
    # -------------------------------------
    jd_full = "Looking for a backend engineer with Python, Django, and cloud experience."
    jd_skills = ["Python", "Django", "AWS", "SQL"]
    jd_experience = "Minimum 4 years of backend engineering experience building REST APIs."
    
    # Candidate 1: Perfect Match
    res1_full = "Experienced backend developer proficient in Python, Django REST framework, and AWS deployment."
    res1_skills = "Python, Django, PostgreSQL, AWS EC2, Git"
    res1_exp = "5 years working as a backend software engineer building scalable REST APIs."
    
    # Candidate 2: Completely Irrelevant
    res2_full = "Graphic designer creating UI/UX wireframes and marketing assets."
    res2_skills = "Photoshop, Figma, Illustrator, Adobe Creative Cloud"
    res2_exp = "3 years designing web interfaces and print media."
    
    # -------------------------------------
    # Execution
    # -------------------------------------
    print("\n[+] Computing similarities for Strong Candidate (Backend Dev)...")
    match1 = matcher.match_candidate(
        jd_full_text=jd_full, jd_skills=jd_skills, jd_experience=jd_experience,
        resume_full_text=res1_full, resume_skills=res1_skills, resume_experience=res1_exp
    )
    
    print("[+] Computing similarities for Weak Candidate (Graphic Designer)...")
    match2 = matcher.match_candidate(
        jd_full_text=jd_full, jd_skills=jd_skills, jd_experience=jd_experience,
        resume_full_text=res2_full, resume_skills=res2_skills, resume_experience=res2_exp
    )
    
    # -------------------------------------
    # Validation & Output
    # -------------------------------------
    print("\n" + "="*50)
    print("RESULTS")
    print("="*50)
    print("Candidate 1 (Strong Match):")
    print(f"  🟢 Overall:    {match1['overall_similarity']:.4f}")
    print(f"  🟢 Skills:     {match1['skills_similarity']:.4f}")
    print(f"  🟢 Experience: {match1['experience_similarity']:.4f}")
    
    print("\nCandidate 2 (Weak Match):")
    print(f"  🔴 Overall:    {match2['overall_similarity']:.4f}")
    print(f"  🔴 Skills:     {match2['skills_similarity']:.4f}")
    print(f"  🔴 Experience: {match2['experience_similarity']:.4f}")

    assert match1["overall_similarity"] > match2["overall_similarity"], "Logic Error!"
    print("\n✅ Semantic Matcher accurately differentiated the strong and weak candidate!")

if __name__ == "__main__":
    test_semantic_matcher()
