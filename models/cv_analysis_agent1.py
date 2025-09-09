from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from sqlalchemy.sql import func
from config.database import Base
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class CVAnalysisRecord(Base):
    """SQLAlchemy model for storing CV analysis results in TiDB"""
    __tablename__ = "cv_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True)
    cv_filename = Column(String(255))
    job_title = Column(String(255))
    company = Column(String(255), nullable=True)
    
    # Analysis results stored as JSON
    extracted_skills = Column(JSON)
    extracted_experience = Column(JSON)
    education = Column(JSON)
    
    # Gap analysis results
    skill_gaps = Column(JSON)
    experience_gaps = Column(JSON)
    match_score = Column(Float)
    recommendations = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models for API requests/responses
class CVUploadRequest(BaseModel):
    user_id: str
    job_description: str
    job_title: str
    company: Optional[str] = None

class SkillGap(BaseModel):
    missing_skill: str
    importance: str  # "critical", "important", "nice-to-have"
    suggested_resources: List[str]

class CVAnalysisResult(BaseModel):
    id: int
    user_id: str
    cv_filename: str
    job_title: str
    company: Optional[str]
    
    extracted_skills: List[str]
    extracted_experience: List[Dict[str, str]]
    education: List[Dict[str, str]]
    
    skill_gaps: List[SkillGap]
    experience_gaps: List[str]
    match_score: float
    recommendations: List[str]
    
    created_at: datetime

class AgentHandoffData(BaseModel):
    """Data structure for passing info from Agent 1 to Agent 2"""
    analysis_id: int
    user_id: str
    skill_gaps: List[SkillGap]
    experience_gaps: List[str]
    match_score: float
    target_role: str
    priority_skills: List[str]