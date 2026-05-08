from pydantic import BaseModel, Field
from typing import List, Optional

class JobDescription(BaseModel):
    required_skills: List[str] = Field(description="List of required technical and soft skills")
    years_of_experience: int = Field(description="Minimum years of experience required")
    qualifications: List[str] = Field(description="Required educational qualifications or certifications")
    responsibilities: List[str] = Field(description="Key job responsibilities")
    preferred_technologies: List[str] = Field(description="Preferred but not strictly required technologies")
    seniority_level: str = Field(description="Seniority level (e.g., Junior, Mid, Senior)")

class DimensionScore(BaseModel):
    score: int = Field(description="Score from 0 to 10 for this dimension")
    justification: str = Field(description="One-line justification for the score")

class CandidateScore(BaseModel):
    skills_match: DimensionScore = Field(description="Weight: 30%")
    experience_relevance: DimensionScore = Field(description="Weight: 25%")
    education_certs: DimensionScore = Field(description="Weight: 15%")
    project_portfolio: DimensionScore = Field(description="Weight: 20%")
    communication_quality: DimensionScore = Field(description="Weight: 10%")
    weighted_total_score: float = Field(description="Total score calculated based on dimension weights")
    recommendation: str = Field(description="Must be 'Hire' or 'No-Hire'")

class CandidateReport(BaseModel):
    candidate_id: str
    candidate_name: str
    score_breakdown: CandidateScore
    is_overridden: bool = False
    override_reason: Optional[str] = None
