from typing import Dict, Any, List
import json
import re
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

class QnAAgent:
    def __init__(self, llm_agent):
        self.agent = llm_agent

    def generate_questions(
        self, 
        cv_data: Dict[str, Any], 
        jd_data: Dict[str, Any], 
        comparison: Dict[str, Any]
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        Generate recruiter-style questions grouped by skill and level:
        - Level 1: Basic theory checks
        - Level 2: Practical/project validation
        - Level 3: Advanced, problem-solving, missing JD skills
        """
        prompt = f"""
        You are a recruiter preparing candidate screening questions.

        Data:
        CV Data:
        {cv_data}

        JD Data:
        {jd_data}

        CV vs JD Comparison:
        {comparison}

        Instructions:
        - For EACH relevant skill (from CV, JD, or comparison), generate 2–3 questions per level.
        - Structure output by skill and level:

        {{
          "Python": {{
            "Level 1": ["Q1", "Q2"],
            "Level 2": ["Q1", "Q2"],
            "Level 3": ["Q1", "Q2"]
          }},
          "SQL": {{
            "Level 1": ["Q1", "Q2"],
            "Level 2": ["Q1", "Q2"],
            "Level 3": ["Q1", "Q2"]
          }}
        }}

        - Levels meaning:
          Level 1 (Basic Theory): Simple concept checks, short direct.
          Level 2 (Practical Application): Real project usage or scenario.
          Level 3 (Advanced/Missing Skills): Complex challenges, optimization, missing JD skills.

        - Cover:
          * CV skills (L1+L2)
          * Missing JD skills (L3)
          * Extra CV skills (L2 or L3, if relevant)
        - Return ONLY valid JSON.
        """

        result = self.agent.run(prompt)
        raw = result.content if hasattr(result, "content") else str(result)

        # Clean up any ```json ... ``` wrappers
        cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

        try:
            questions = json.loads(cleaned)
            if not isinstance(questions, dict):
                raise ValueError("Expected a dict grouped by skill → levels")
        except Exception:
            # fallback nếu model trả về hỏng format
            questions = {"General": {"Level 1": [], "Level 2": [], "Level 3": [cleaned]}}

        return questions

    def save_answers(
        self, 
        candidate_id: str, 
        questions: Dict[str, Dict[str, List[str]]], 
        answers: Dict[str, Dict[str, List[str]]]
    ) -> Dict[str, Any]:
        qa_pairs = {
            skill: {
                level: [
                    {"question": q, "answer": a} 
                    for q, a in zip(questions[skill][level], answers.get(skill, {}).get(level, []))
                ]
                for level in questions[skill]
            }
            for skill in questions
        }
        return {
            "candidate_id": candidate_id,
            "qa_pairs": qa_pairs
        }


if __name__ == "__main__":
    cv_data = {
        "Skills": "Python, SQL, Data Visualization, Machine Learning, Deep Learning, Tableau, TensorFlow, Data Analysis",
        "Education": "Master of Data Science, University of Toronto, 2020\nBachelor of Computer Science, ABC University, 2018",
        "Experience": "Data Scientist, FinTech Solutions Inc, 2020–2024\n- Built predictive models...\n\nData Analyst, Retail Insights Ltd, 2018–2020..."
    }

    jd_data = {
        "Skills": "Python, SQL, Machine Learning, Communication, Cloud Platforms (AWS or GCP), Data Engineering",
        "Qualifications": "Master’s degree in Computer Science, Data Science, or related field\n3+ years of professional experience in data-focused roles",
        "Responsibilities": "- Design and implement scalable ML models...\n- Work with cross-functional teams...\n- Maintain data pipelines..."
    }

    comparison = {
        "Skills": {
            "Matched": ["Python", "SQL", "Machine Learning"],
            "Missing (JD)": ["Cloud Platforms (AWS or GCP)", "Data Engineering"],
            "Extra (CV)": ["Data Visualization", "Deep Learning", "Tableau", "TensorFlow", "Data Analysis"]
        },
        "Qualifications": {
            "Matched": ["Master’s degree in Data Science"],
            "Missing (JD)": [],
            "Extra (CV)": ["Bachelor of Computer Science"]
        },
        "Responsibilities": {
            "Matched": [
                "Design and implement scalable ML models",
                "Work with cross-functional teams to translate business requirements into data-driven solutions",
                "Communicate findings and insights effectively to both technical and non-technical audiences"
            ],
            "Missing (JD)": ["Maintain data pipelines and ensure high-quality data availability"],
            "Extra (CV)": []
        },
        "Education": {
            "Matched": ["Master of Data Science"],
            "Missing (JD)": [],
            "Extra (CV)": ["Bachelor of Computer Science, ABC University, 2018"]
        },
        "Experience": {
            "Matched": ["Data Scientist", "Data Analyst"],
            "Missing (JD)": [],
            "Extra (CV)": []
        }
    }

    model_id = "gemini-1.5-flash-latest"
    llm_agent = Agent(
        model=Gemini(id=model_id),
        description="Recruiter QnA generator grouped by skills and levels",
        instructions="Generate recruiter-style clarification questions grouped by skill and level.",
        show_tool_calls=False
    )

    agent = QnAAgent(llm_agent)
    questions = agent.generate_questions(cv_data, jd_data, comparison)
    print(json.dumps(questions, indent=2, ensure_ascii=False))
