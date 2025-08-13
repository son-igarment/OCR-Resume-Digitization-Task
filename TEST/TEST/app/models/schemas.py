from typing import List, Optional
from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    company: Optional[str] = Field(default=None)
    position: Optional[str] = Field(default=None)
    duration: Optional[str] = Field(default=None)


class CandidateResume(BaseModel):
    name: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    birth_date: Optional[str] = Field(default=None, description="ISO date YYYY-MM-DD if detected")
    experience: List[ExperienceItem] = Field(default_factory=list) 