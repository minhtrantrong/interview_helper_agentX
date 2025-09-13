from typing import Dict, Any, List
import json
import re
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

class InterviewScriptAgent:
    """
    Agent #5: Generate structured interview scripts for voice interviewing based on 
    questions from previous agents. Creates conversational flows with follow-ups,
    transitions, and evaluation criteria for voice-based interviews.
    """
    
    def __init__(self, model_id: str = "gemini-1.5-flash-latest"):
        self.model = Gemini(id=model_id)
        self.agent = Agent(
            model=self.model,
            description=(
                "You are an expert interview script generator that creates structured "
                "conversational flows for voice-based candidate interviews."
            ),
            instructions=(
                "Generate comprehensive interview scripts that include:\n"
                "1. Opening statements and candidate warm-up\n"
                "2. Question sequences with natural transitions\n"
                "3. Follow-up prompts and probing questions\n"
                "4. Time allocations and pacing guidelines\n"
                "5. Evaluation criteria and scoring notes\n"
                "6. Closing statements and next steps\n"
                "Format output as structured JSON with conversational flow."
            ),
            show_tool_calls=False
        )
    
    def generate_interview_script(
        self,
        questions: Dict[str, Any],
        cv_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        interview_duration: int = 30,
        interview_type: str = "technical"
    ) -> Dict[str, Any]:
        """
        Generate a complete interview script for voice interviewing.
        
        Args:
            questions: Questions from previous agents (structured or flat list)
            cv_data: Candidate CV data
            jd_data: Job description data
            interview_duration: Interview length in minutes
            interview_type: "technical", "behavioral", "mixed"
        """
        
        candidate_name = self._extract_candidate_name(cv_data)
        role_title = self._extract_role_title(jd_data)
        
        prompt = f"""
        Create a comprehensive voice interview script for a {interview_duration}-minute {interview_type} interview.
        
        Candidate: {candidate_name}
        Role: {role_title}
        
        Questions to incorporate:
        {json.dumps(questions, indent=2)}
        
        CV Summary:
        {self._summarize_cv(cv_data)}
        
        JD Summary:
        {self._summarize_jd(jd_data)}
        
        Generate a structured interview script with this JSON format:
        {{
            "interview_metadata": {{
                "candidate_name": "{candidate_name}",
                "role": "{role_title}",
                "duration_minutes": {interview_duration},
                "type": "{interview_type}",
                "total_questions": 0,
                "difficulty_distribution": {{"easy": 0, "medium": 0, "hard": 0}}
            }},
            "script_sections": {{
                "opening": {{
                    "duration_minutes": 2,
                    "interviewer_intro": "...",
                    "agenda_overview": "...",
                    "candidate_comfort_check": "..."
                }},
                "main_interview": {{
                    "sections": [
                        {{
                            "section_name": "Technical Skills Assessment",
                            "duration_minutes": 15,
                            "questions": [
                                {{
                                    "primary_question": "...",
                                    "follow_ups": ["...", "..."],
                                    "evaluation_criteria": ["...", "..."],
                                    "difficulty": "medium",
                                    "time_allocation": 3,
                                    "notes_for_interviewer": "..."
                                }}
                            ]
                        }}
                    ]
                }},
                "closing": {{
                    "duration_minutes": 3,
                    "candidate_questions_time": "...",
                    "next_steps_explanation": "...",
                    "thank_you_closing": "..."
                }}
            }},
            "interviewer_guidelines": {{
                "voice_tone": "professional yet conversational",
                "pacing_notes": "...",
                "transition_phrases": ["...", "..."],
                "difficult_situation_handling": "..."
            }},
            "scoring_framework": {{
                "evaluation_areas": [
                    {{
                        "area": "Technical Competency",
                        "weight": 0.4,
                        "criteria": ["...", "..."]
                    }}
                ],
                "scoring_scale": "1-5 scale with detailed rubric",
                "overall_recommendation_guide": "..."
            }}
        }}
        
        Requirements:
        - Create natural conversation flow with smooth transitions
        - Include time management guidance
        - Provide specific follow-up questions for deeper probing
        - Add evaluation criteria for each question
        - Include handling tips for different candidate responses
        - Ensure total time adds up to {interview_duration} minutes
        - Balance question difficulty appropriately
        - Include voice interview specific considerations (clarity, pace, etc.)
        """
        
        result = self.agent.run(prompt)
        raw = result.content if hasattr(result, "content") else str(result)
        
        # Clean up JSON formatting
        cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
        
        try:
            script = json.loads(cleaned)
            return script
        except Exception as e:
            # Fallback structure if JSON parsing fails
            return {
                "interview_metadata": {
                    "candidate_name": candidate_name,
                    "role": role_title,
                    "duration_minutes": interview_duration,
                    "type": interview_type,
                    "parsing_error": str(e)
                },
                "raw_output": cleaned,
                "questions": questions
            }
    
    def generate_question_scripts(
        self,
        questions: List[str],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Convert a simple list of questions into detailed interview script items.
        """
        
        prompt = f"""
        Convert these interview questions into detailed script items for voice interviewing:
        
        Questions:
        {json.dumps(questions, indent=2)}
        
        Context (if available):
        {json.dumps(context or {}, indent=2)}
        
        For each question, provide:
        {{
            "primary_question": "Original question rephrased for natural conversation",
            "follow_ups": ["2-3 follow-up questions"],
            "evaluation_criteria": ["What to listen for in the answer"],
            "difficulty": "easy/medium/hard",
            "estimated_time": "minutes",
            "interviewer_notes": "Tips for asking this question effectively"
        }}
        
        Return as JSON array of question objects.
        """
        
        result = self.agent.run(prompt)
        raw = result.content if hasattr(result, "content") else str(result)
        cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
        
        try:
            return json.loads(cleaned)
        except Exception:
            # Fallback: convert questions to basic format
            return [
                {
                    "primary_question": q,
                    "follow_ups": ["Can you elaborate on that?", "What challenges did you face?"],
                    "evaluation_criteria": ["Clarity of explanation", "Depth of knowledge"],
                    "difficulty": "medium",
                    "estimated_time": 3,
                    "interviewer_notes": "Listen for specific examples and problem-solving approach"
                }
                for q in questions
            ]
    
    def create_voice_guidelines(
        self,
        interview_type: str = "technical",
        candidate_level: str = "mid"
    ) -> Dict[str, Any]:
        """
        Generate specific guidelines for conducting voice interviews.
        """
        
        prompt = f"""
        Create comprehensive voice interview guidelines for a {interview_type} interview 
        with a {candidate_level}-level candidate.
        
        Include:
        1. Voice and tone recommendations
        2. Pacing and timing guidance  
        3. Handling technical difficulties
        4. Reading candidate vocal cues
        5. Creating rapport in audio-only environment
        6. Question delivery techniques
        7. Note-taking strategies during voice calls
        
        Return as structured JSON with actionable guidance.
        """
        
        result = self.agent.run(prompt)
        raw = result.content if hasattr(result, "content") else str(result)
        cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
        
        try:
            return json.loads(cleaned)
        except Exception:
            return {
                "voice_tone": "Professional, warm, and encouraging",
                "pacing": "Speak clearly and allow pauses for candidate responses",
                "technical_issues": "Have backup communication method ready",
                "rapport_building": "Use candidate's name frequently and acknowledge their responses",
                "raw_output": cleaned
            }
    
    # Helper methods
    def _extract_candidate_name(self, cv_data: Dict[str, Any]) -> str:
        """Extract candidate name from CV data."""
        # Look for common name patterns in CV text
        cv_text = str(cv_data)
        name_patterns = [
            r"Name[:\s]*([A-Z][a-z]+ [A-Z][a-z]+)",
            r"^([A-Z][a-z]+ [A-Z][a-z]+)",  # First line name
            r"([A-Z][a-z]+ [A-Z][a-z]+)"  # Any two capitalized words
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, cv_text)
            if match:
                return match.group(1)
        
        return "Candidate"
    
    def _extract_role_title(self, jd_data: Dict[str, Any]) -> str:
        """Extract role title from job description."""
        jd_text = str(jd_data)
        
        # Look for common role title patterns
        role_patterns = [
            r"(?:Position|Role|Title)[:\s]*([A-Z][a-zA-Z ]+)",
            r"([A-Z][a-zA-Z ]+ (?:Engineer|Developer|Scientist|Analyst|Manager))",
            r"We are looking for (?:a |an )?([A-Z][a-zA-Z ]+)"
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, jd_text)
            if match:
                return match.group(1)
        
        return "Position"
    
    def _summarize_cv(self, cv_data: Dict[str, Any]) -> str:
        """Create a brief CV summary for context."""
        skills = cv_data.get("Skills", "")
        experience = cv_data.get("Experience", "")
        education = cv_data.get("Education", "")
        
        return f"Skills: {skills[:100]}...\nExperience: {experience[:100]}...\nEducation: {education[:100]}..."
    
    def _summarize_jd(self, jd_data: Dict[str, Any]) -> str:
        """Create a brief JD summary for context."""
        requirements = jd_data.get("Skills", "") or jd_data.get("Requirements", "")
        responsibilities = jd_data.get("Responsibilities", "")
        
        return f"Requirements: {requirements[:100]}...\nResponsibilities: {responsibilities[:100]}..."


if __name__ == "__main__":
    # Example usage with questions from previous agents
    sample_questions = {
        "Python": {
            "Level 1": [
                "What are the main data types in Python?",
                "Explain the difference between lists and tuples"
            ],
            "Level 2": [
                "Describe a project where you used Python for data analysis",
                "How do you handle exceptions in Python?"
            ],
            "Level 3": [
                "Explain Python's GIL and its implications",
                "How would you optimize a slow Python script?"
            ]
        },
        "SQL": {
            "Level 1": [
                "What is the difference between INNER JOIN and LEFT JOIN?",
                "How do you filter data using WHERE clause?"
            ],
            "Level 2": [
                "Describe a complex query you've written for data extraction",
                "How do you optimize SQL query performance?"
            ]
        }
    }
    
    cv_data = {
        "Skills": "Python, SQL, Data Analysis, Machine Learning",
        "Experience": "Data Scientist at TechCorp, 3 years experience building ML models",
        "Education": "Master's in Computer Science"
    }
    
    jd_data = {
        "Skills": "Python, SQL, Machine Learning, Communication",
        "Responsibilities": "Build data models, analyze business metrics, present findings"
    }
    
    agent = InterviewScriptAgent()
    
    # Generate complete interview script
    script = agent.generate_interview_script(
        questions=sample_questions,
        cv_data=cv_data,
        jd_data=jd_data,
        interview_duration=30,
        interview_type="technical"
    )
    
    print("Generated Interview Script:")
    print(json.dumps(script, indent=2, ensure_ascii=False))
    
    # Generate voice guidelines
    guidelines = agent.create_voice_guidelines("technical", "mid")
    print("\nVoice Interview Guidelines:")
    print(json.dumps(guidelines, indent=2, ensure_ascii=False))