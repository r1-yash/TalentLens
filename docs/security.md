 # Security Mitigations

As per the mandatory requirements, this project implements the following security measures:

| Risk | Mitigation Strategy |
|------|----------------------|
| **Prompt Injection** | Input sanitization, strict Pydantic structured output schemas, and output parsers with validation. System prompts are strongly typed and user inputs are enclosed in XML-style tags. |
| **Data Privacy / PII** | Resumes are processed locally where possible. Semantic matching runs on local `sentence-transformers` to avoid sending raw text to cloud APIs. Log masking is implemented for sensitive fields. |
| **API Key Exposure** | Use of `python-dotenv` and `.env` file (which is gitignored). No hardcoded secrets in source code. |
| **Hallucination Risk** | Forced structured JSON output via Pydantic. Human-in-the-loop review step implemented via Streamlit to verify and override scores. |
| **Unauthorized Access** | FastAPI endpoints protected via API key authentication. |
