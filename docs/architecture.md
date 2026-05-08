# Project Architecture

The architecture is built on a Multi-Agent State Graph approach using LangGraph.

## Core Agents Workflow

1. **JDParsingAgent**:
   - **Input**: Raw text from JD document.
   - **Action**: Uses LLM Structured Output.
   - **Output**: `JobDescription` Pydantic model (Skills, Exp, Qualifications).

2. **ResumeIngestionAgent**:
   - **Input**: PDF/DOCX files.
   - **Action**: Text extraction using `PyMuPDF`/`python-docx`, text sanitization.
   - **Output**: Cleaned text strings per candidate.

3. **Semantic Matching Engine**:
   - **Input**: JD Text, Resume Text.
   - **Action**: Encodes text using local `sentence-transformers`. Computes FAISS Cosine Similarity.
   - **Output**: Semantic similarity score (used as a feature for the LLM).

4. **CandidateScoringAgent**:
   - **Input**: `JobDescription`, Cleaned Resume Text, Semantic Score.
   - **Action**: Prompts the LLM with the mandatory 5-dimension rubric. Forces output into `CandidateScore` Pydantic schema.
   - **Output**: Dimension scores (0-10), total weighted score, hire/no-hire flag, one-line justifications.

5. **Report Generation Agent**:
   - **Input**: Aggregated `CandidateScore` models.
   - **Action**: Ranks by weighted score, formats into JSON and HTML strings.
   - **Output**: Final `CandidateReport` payloads.

## Data Flow Diagram

```text
[Streamlit UI]
      | (Uploads JD & Resumes)
      v
[FastAPI Backend - /upload]
      |
      +---> [JD Parser Agent] ---> (JobDescription Schema)
      |                                  |
      +---> [Resume Parser] ---> (Raw Text Arrays)
                                         |
                                         v
                         [Semantic Matching & Scoring Agent]
                                         |
                                         v
                                (CandidateScore Schemas)
                                         |
                                         v
[Report Generation] <------------- [Ranking Engine]
      |
      v
[Streamlit UI] ---> (Displays Leaderboard & Scores)
      |
      +---> [Human Override] ---> (Sends adjustment to FastAPI /override)
```
