from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import os
import tempfile
from typing import Optional

from config.database import get_db, engine
from models.cv_analysis import CVAnalysisResult, AgentHandoffData
from agents.cv_analyzer import CVAnalyzerAgent
from utils.database_init import create_tables

app = FastAPI(
    title="Interview Prep Multi-Agent System",
    description="TiDB Hackathon - Multi-agent AI system for interview preparation",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.post("/upload-cv", response_model=AgentHandoffData)
async def analyze_cv(
    cv_file: UploadFile = File(...),
    user_id: str = Form(...),
    job_description: str = Form(...),
    job_title: str = Form(...),
    company: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Agent 1: Analyze CV/Resume against job description
    Returns structured data for Agent 2 (recommendation engine)
    """
    
    # Validate file type
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
    file_extension = os.path.splitext(cv_file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Use: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        shutil.copyfileobj(cv_file.file, temp_file)
        temp_file_path = temp_file.name
    
    try:
        # Initialize CV Analyzer Agent
        analyzer = CVAnalyzerAgent(db)
        
        # Analyze CV and generate handoff data for Agent 2
        handoff_data = analyzer.analyze_cv_and_job(
            cv_file_path=temp_file_path,
            job_description=job_description,
            user_id=user_id,
            job_title=job_title,
            company=company
        )
        
        return handoff_data
    
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

@app.get("/analysis/{analysis_id}", response_model=CVAnalysisResult)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get saved CV analysis results"""
    from models.cv_analysis import CVAnalysisRecord
    
    analysis = db.query(CVAnalysisRecord).filter(CVAnalysisRecord.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return CVAnalysisResult(
        id=analysis.id,
        user_id=analysis.user_id,
        cv_filename=analysis.cv_filename,
        job_title=analysis.job_title,
        company=analysis.company,
        extracted_skills=analysis.extracted_skills,
        extracted_experience=analysis.extracted_experience,
        education=analysis.education,
        skill_gaps=analysis.skill_gaps,
        experience_gaps=analysis.experience_gaps,
        match_score=analysis.match_score,
        recommendations=analysis.recommendations,
        created_at=analysis.created_at
    )

@app.get("/user/{user_id}/analyses")
async def get_user_analyses(user_id: str, db: Session = Depends(get_db)):
    """Get all analyses for a specific user"""
    from models.cv_analysis import CVAnalysisRecord
    
    analyses = db.query(CVAnalysisRecord).filter(CVAnalysisRecord.user_id == user_id).all()
    
    return [{"id": a.id, "job_title": a.job_title, "company": a.company, 
             "match_score": a.match_score, "created_at": a.created_at} for a in analyses]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "interview-prep-agents"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)