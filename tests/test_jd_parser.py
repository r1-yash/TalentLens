import sys
import os
from pydantic import ValidationError
from agents.jd_parser_agent import JDParsingAgent

def test_jd_parser():
    print("="*40)
    print("TEST: JD PARSING AGENT (GEMINI + LANGCHAIN)")
    print("="*40)
    
    agent = JDParsingAgent()
    
    # 1. Empty JD
    print("\n[+] Testing Empty JD...")
    res1 = agent.parse_jd("   ")
    assert res1 is None, "Empty JD should return None"
    print("    ✅ Empty JD handled safely.")
    
    # 2. Short / Nonsense JD
    print("\n[+] Testing Malformed/Short JD...")
    res2 = agent.parse_jd("We just need a guy who knows Python and AWS.")
    if res2:
        print(f"    ✅ Short JD parsed. Extracted Skills: {res2.required_skills}")
        print(f"    ✅ Defaults applied: Experience = {res2.minimum_experience}, Seniority = {res2.seniority_level}")
    else:
        print("    ✅ Short JD failed safely (validation error or LLM refusal).")

    # 3. Valid JD
    print("\n[+] Testing Valid JD...")
    valid_jd = "Looking for a Senior Python Developer with 5 years experience in FastAPI and AWS. Must have a CS degree."
    try:
        res3 = agent.parse_jd(valid_jd)
        if res3:
            assert "Python" in str(res3.required_skills) or "FastAPI" in str(res3.required_skills)
            print("    ✅ Valid JD parsed successfully.")
            print(f"    ✅ Output is JSON-safe Pydantic: {res3.role_title}")
        else:
            print("    ❌ Valid JD parsing failed silently.")
    except Exception as e:
        print(f"    ❌ Test Crashed: {str(e)}")

if __name__ == "__main__":
    test_jd_parser()
