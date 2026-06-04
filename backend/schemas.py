from pydantic import BaseModel, Field
from typing import List

class SkillCategory(BaseModel):
    category: str
    items: List[str]

class ResumeProject(BaseModel):
    name: str
    description: str


class ResumeEducation(BaseModel):
    degree: str
    university: str
    year: str


class ResumeCertification(BaseModel):
    name: str
    description: str


class ATSResumeSchema(BaseModel):
    summary: str
    skills: List[SkillCategory]
    experience: List[str]
    projects: List[ResumeProject]
    education: List[ResumeEducation]
    certifications: List[ResumeCertification]


class ATSOptimizationSchema(BaseModel):
    ats_resume: ATSResumeSchema
    ats_cover_letter: str
    keywords_used: List[str]
    formatting_notes: List[str]