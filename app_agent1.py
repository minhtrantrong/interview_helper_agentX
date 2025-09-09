#!/usr/bin/env python3
"""
TiDB Hackathon - Multi-Agent Interview Prep System
Agent 1: CV/Resume Analysis Engine

Production Entry Point
"""
import sys
import os
sys.path.append('.')

from sqlalchemy.orm import Session
from config.database import SessionLocal
from agents.cv_analyzer import CVAnalyzerAgent
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_cv_for_job(cv_file_path: str, job_description: str, user_id: str, job_title: str, company: str = None):
    """
    Main function to analyze a CV against a job description
    
    Args:
        cv_file_path (str): Path to the CV file (PDF, DOCX, TXT, etc.)
        job_description (str): The job posting text
        user_id (str): Unique identifier for the user
        job_title (str): Title of the target position
        company (str, optional): Company name
        
    Returns:
        dict: Analysis results with match score, skill gaps, and recommendations
    """
    
    logger.info("🚀 Starting CV Analysis")
    logger.info(f"   📄 CV: {cv_file_path}")
    logger.info(f"   🎯 Position: {job_title} at {company or 'Unknown Company'}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Initialize Agent 1
        analyzer = CVAnalyzerAgent(db)
        
        # Analyze CV against job
        handoff_data = analyzer.analyze_cv_and_job(
            cv_file_path=cv_file_path,
            job_description=job_description,
            user_id=user_id,
            job_title=job_title,
            company=company
        )
        
        # Convert to dictionary for easy consumption
        result = {
            "analysis_id": handoff_data.analysis_id,
            "user_id": handoff_data.user_id,
            "target_role": handoff_data.target_role,
            "match_score": handoff_data.match_score,
            "match_percentage": f"{handoff_data.match_score * 100:.1f}%",
            "priority_skills": handoff_data.priority_skills,
            "skill_gaps": [
                {
                    "missing_skill": gap.missing_skill,
                    "importance": gap.importance,
                    "suggested_resources": gap.suggested_resources
                }
                for gap in handoff_data.skill_gaps
            ],
            "experience_gaps": handoff_data.experience_gaps
        }
        
        logger.info(f"✅ Analysis complete! Match score: {result['match_percentage']}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise e
    
    finally:
        db.close()

def demo_analysis():
    """Run demo analysis with sample data"""
    
    print("🎯 AGENT 1 DEMO - CV Analysis Engine")
    print("=" * 50)
    
    # Use sample files
    cv_path = "data/sample_cv.txt"
    
    with open("data/sample_job.txt", "r") as f:
        job_description = f.read()
    
    try:
        # Run analysis
        result = analyze_cv_for_job(
            cv_file_path=cv_path,
            job_description=job_description,
            user_id="demo_user",
            job_title="Digital Marketing Manager",
            company="GrowthTech Solutions"
        )
        
        # Display results
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   🎯 Position: {result['target_role']}")
        print(f"   📈 Match Score: {result['match_percentage']}")
        print(f"   ⚠️  Skill Gaps: {len(result['skill_gaps'])}")
        print(f"   💼 Experience Gaps: {len(result['experience_gaps'])}")
        
        print(f"\n🔍 TOP SKILL GAPS:")
        for i, gap in enumerate(result['skill_gaps'][:3], 1):
            print(f"   {i}. {gap['missing_skill']} ({gap['importance']})")
        
        print(f"\n💾 Analysis ID: {result['analysis_id']} (saved to TiDB)")
        print(f"\n🚀 Ready for Agent 2 handoff!")
        
        return result
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return None

if __name__ == "__main__":
    demo_analysis()