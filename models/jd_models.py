from pydantic import BaseModel, Field
from typing import List

class JobDescriptionData(BaseModel):
    role_title: str = Field(description="The formal title of the role")
    required_skills: List[str] = Field(description="Strictly required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have skills")
    minimum_experience: int = Field(description="Minimum years of experience required. 0 if not specified.", default=0)
    education_requirements: List[str] = Field(default_factory=list, description="Required education or degrees")
    responsibilities: List[str] = Field(description="Key responsibilities of the role")
    tools_and_technologies: List[str] = Field(default_factory=list, description="Specific software, tools, or tech stack mentioned")
    seniority_level: str = Field(description="Seniority level (e.g., Junior, Mid, Senior, Lead, Executive)", default="Unspecified")
