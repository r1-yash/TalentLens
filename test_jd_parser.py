# THIS IS MY COMPLETE SYNTHETIC JD FOR TESTING PURPOSE

import os
import json
from dotenv import load_dotenv

# Load env variables (like GOOGLE_API_KEY) before importing the agent
load_dotenv()

from agents.jd_parser_agent import JDParsingAgent

sample_jd_text = """
Job Title: Senior Software Engineer (Python/FastAPI)
Location: Remote
About Us: We are building the future of AI tools.

Role Requirements:
- At least 5 years of experience in backend development.
- Strong proficiency in Python, FastAPI, and SQL.
- Experience with Docker, Kubernetes, and AWS is preferred.
- Bachelor's degree in Computer Science or related field.

Responsibilities:
- Design and build scalable REST APIs.
- Collaborate with frontend engineers to integrate Streamlit UIs.
- Write unit and integration tests.

Seniority: Senior
"""

def test_parser():
    # Pre-flight check
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ ERROR: GOOGLE_API_KEY is not set in your .env file.")
        print("Please add it to test the Gemini integration.")
        return

    agent = JDParsingAgent()
    
    print("\n" + "="*40)
    print("RAW JOB DESCRIPTION INPUT")
    print("="*40)
    print(sample_jd_text.strip())
    
    print("\n" + "="*40)
    print("AGENT EXTRACTION IN PROGRESS...")
    print("="*40)
    
    parsed_data = agent.parse_jd(sample_jd_text)
    
    if parsed_data:
        print("\n✅ EXTRACTION SUCCESSFUL:")
        # Print JSON output safely
        print(json.dumps(parsed_data.model_dump(), indent=2))
    else:
        print("\n❌ EXTRACTION FAILED. Check logs.")

if __name__ == "__main__":
    test_parser()
