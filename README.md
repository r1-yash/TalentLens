# HR Resume & LinkedIn Shortlisting Agent

An AI-powered system designed to assist HR teams in evaluating candidates efficiently. This agent ingests a Job Description (JD) alongside multiple resumes, computing a structured scoring rubric and producing a ranked shortlist, all while keeping a human in the loop.

## Overview

HR teams face fatigue and bias when screening hundreds of applications. This system standardizes the process by:
1. Parsing Job Descriptions for required skills, experience, and qualifications.
2. Ingesting resumes (PDF/DOCX) or LinkedIn data.
3. Conducting semantic matching and LLM-driven scoring against a mandatory 5-dimension rubric.
4. Providing a transparent, highly structured score breakdown with justifications.
5. Offering a Human-in-the-Loop UI to override and log score adjustments.

## Tech Stack & Decision Log

| Layer | Selected Tech | Rationale |
|---|---|---|
| **LLM** | Gemini API (`gemini-1.5-flash`) | We selected Gemini Flash because it provides a strong free-tier option suitable for rapid AI agent prototyping. It fully supports structured outputs via Pydantic which is crucial for our pipeline. |
| **Agent Framework** | LangGraph / LangChain | LangGraph manages cyclic workflows perfectly. The multi-step nature of HR evaluation (Extract -> Read -> Score -> Rank) requires state management across steps. |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | Local, private, and highly performant for cosine similarity. Avoids sending massive raw candidate data to cloud endpoints just for embedding. |
| **Backend API** | FastAPI | Asynchronous, natively integrates with Pydantic for data validation, and generates automatic OpenAPI swagger docs for the frontend to consume. |
| **Frontend UI** | Streamlit | Perfect for rapidly prototyping data-heavy dashboards, forms, and Human-in-the-Loop mechanisms. |
| **Parsing** | `pdfplumber` (PDF), `python-docx` (Word) | Most reliable extractors for varied document structures, with full Python 3.13/macOS native compatibility without complex C compiler dependencies. |

## Quick Start
*Setup instructions will be populated here as we build out the modules.*

1. Copy `.env.example` to `.env` and fill in credentials.
2. Install requirements: `pip install -r requirements.txt`
3. Run Backend: `uvicorn main:app --reload`
4. Run Frontend: `streamlit run app.py`

## Security Mitigations
Refer to `docs/security.md` for a comprehensive breakdown of Prompt Injection, PII handling, and hallucination controls.
