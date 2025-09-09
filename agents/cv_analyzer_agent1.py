import json
import re
import logging
from typing import List, Dict, Any
from models.cv_analysis import CVAnalysisRecord, SkillGap, AgentHandoffData
from sqlalchemy.orm import Session
from agents.ai_manager import AIModelManager
from agents.document_parser import DocumentParser

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CVAnalyzerAgent:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.ai_manager = AIModelManager()
        self.document_parser = DocumentParser()
        logger.info("🤖 CV Analyzer Agent initialized with bulletproof AI system")
        logger.info(f"📄 Supported formats: {', '.join(self.document_parser.get_supported_formats())}")
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text using industrial-grade document parser"""
        # Validate file first
        is_valid, validation_msg = self.document_parser.validate_file(file_path)
        if not is_valid:
            logger.error(f"❌ File validation failed: {validation_msg}")
            raise ValueError(f"File validation failed: {validation_msg}")
        
        # Parse the document
        parse_result = self.document_parser.parse_document(file_path)
        
        if not parse_result.success:
            logger.error(f"❌ Document parsing failed: {parse_result.error}")
            raise ValueError(f"Document parsing failed: {parse_result.error}")
        
        # Log parsing details
        logger.info(f"✅ Parsed with {parse_result.method_used}")
        if parse_result.metadata:
            for key, value in parse_result.metadata.items():
                logger.info(f"   📊 {key}: {value}")
        
        return parse_result.text
    
    def analyze_cv_and_job(self, cv_file_path: str, job_description: str, user_id: str, job_title: str, company: str = None) -> AgentHandoffData:
        """Main method to analyze CV against job description"""
        
        # Extract text from CV using industrial-grade parser
        cv_text = self.extract_text_from_file(cv_file_path)
        
        # Use the bulletproof AI manager
        logger.info(f"🔍 Analyzing CV for user: {user_id}")
        logger.info(f"📊 AI Manager Stats: {self.ai_manager.get_stats()}")
        
        # Get analysis from AI manager with fallbacks
        ai_result = self.ai_manager.analyze_cv(cv_text, job_description)
        
        if not ai_result.success:
            logger.error(f"❌ Analysis failed: {ai_result.error}")
            analysis_data = self._fallback_analysis(cv_text, job_description)
        else:
            analysis_data = ai_result.data
            logger.info(f"✅ Analysis successful using {ai_result.model_used}")
            logger.info(f"💰 Cost: ${ai_result.cost:.4f}, Tokens: {ai_result.tokens_used}")
        
        # Save to TiDB
        cv_analysis = CVAnalysisRecord(
            user_id=user_id,
            cv_filename=cv_file_path.split('/')[-1],
            job_title=job_title,
            company=company,
            extracted_skills=analysis_data.get("extracted_skills", []),
            extracted_experience=analysis_data.get("extracted_experience", []),
            education=analysis_data.get("education", []),
            skill_gaps=analysis_data.get("skill_gaps", []),
            experience_gaps=analysis_data.get("experience_gaps", []),
            match_score=analysis_data.get("match_score", 0.0),
            recommendations=analysis_data.get("recommendations", [])
        )
        
        self.db.add(cv_analysis)
        self.db.commit()
        self.db.refresh(cv_analysis)
        
        # Create handoff data for Agent 2
        skill_gaps = [SkillGap(**gap) for gap in analysis_data.get("skill_gaps", [])]
        
        handoff_data = AgentHandoffData(
            analysis_id=cv_analysis.id,
            user_id=user_id,
            skill_gaps=skill_gaps,
            experience_gaps=analysis_data.get("experience_gaps", []),
            match_score=analysis_data.get("match_score", 0.0),
            target_role=job_title,
            priority_skills=self._extract_priority_skills(skill_gaps)
        )
        
        return handoff_data
    
    def _extract_priority_skills(self, skill_gaps: List[SkillGap]) -> List[str]:
        """Extract priority skills based on importance"""
        critical_skills = [gap.missing_skill for gap in skill_gaps if gap.importance == "critical"]
        important_skills = [gap.missing_skill for gap in skill_gaps if gap.importance == "important"]
        return critical_skills + important_skills[:3]  # Top 3 important skills
    
    def _fallback_analysis(self, cv_text: str, job_description: str) -> Dict[str, Any]:
        """Fallback analysis if JSON parsing fails"""
        return {
            "extracted_skills": [],
            "extracted_experience": [],
            "education": [],
            "skill_gaps": [],
            "experience_gaps": [],
            "match_score": 0.5,
            "recommendations": ["Please resubmit for detailed analysis"]
        }