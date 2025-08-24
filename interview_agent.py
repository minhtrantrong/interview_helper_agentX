from typing import Dict, Any, List
import json
import re
from typing import Dict, Any, List
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

class QnAAgent:
    def __init__(self, llm_agent):
        self.agent = llm_agent  # your LLM wrapper (e.g., Gemini, OpenAI, etc.)

    def generate_questions(
        self, 
        cv_data: Dict[str, Any], 
        jd_data: Dict[str, Any], 
        comparison: Dict[str, Any]
    ) -> List[str]:
        """
        Generate clarification questions to ask the candidate based on CV vs JD gaps.
        """
        prompt = f"""
        You are a recruiter preparing candidate screening questions.
        
        Use the following data:
        
        CV Data:
        {cv_data}
        
        JD Data:
        {jd_data}
        
        CV vs JD Comparison:
        {comparison}
        
        Instructions:
        - Generate up to 8 recruiter-style clarification questions. 
        - Focus on missing JD skills, responsibilities, and unclear experience.
        - Also clarify extra skills/experience in CV that may be relevant.
        - Write questions as plain text, not numbered or bulleted.
        - Return ONLY a JSON list of strings.
        """

        result = self.agent.run(prompt)

        try:
            questions = json.loads(
                result.content if hasattr(result, "content") else str(result)
            )
            if not isinstance(questions, list):
                questions = [questions]
        except Exception:
            questions = [result.content if hasattr(result, "content") else str(result)]

        return questions

    def save_answers(
        self, 
        candidate_id: str, 
        questions: List[str], 
        answers: List[str]
    ) -> Dict[str, Any]:
        """
        Save Q&A for a candidate. In real system, replace with DB or persistent storage.
        """
        qa_pairs = [{"question": q, "answer": a} for q, a in zip(questions, answers)]

        # Example storage simulation (replace with DB insert/update)
        saved_data = {
            "candidate_id": candidate_id,
            "qa_pairs": qa_pairs
        }
        return saved_data
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
        "Matched": [
        "Python",
        "SQL",
        "Machine Learning"
        ],
        "Missing (JD)": [
        "Cloud Platforms (AWS or GCP)",
        "Data Engineering"
        ],
        "Extra (CV)": [
        "Data Visualization",
        "Deep Learning",
        "Tableau",
        "TensorFlow",
        "Data Analysis"
        ]
    },
    "Qualifications": {
        "Matched": [
        "Master’s degree in Data Science"
        ],
        "Missing (JD)": [],
        "Extra (CV)": [
        "Bachelor of Computer Science"
        ]
    },
    "Responsibilities": {
        "Matched": [
        "Design and implement scalable ML models",
        "Work with cross-functional teams to translate business requirements into data-driven solutions",
        "Communicate findings and insights effectively to both technical and non-technical audiences"
        ],
        "Missing (JD)": [
        "Maintain data pipelines and ensure high-quality data availability"
        ],
        "Extra (CV)": []
    },
    "Education": {
        "Matched": [
        "Master of Data Science"
        ],
        "Missing (JD)": [],
        "Extra (CV)": [
        "Bachelor of Computer Science, ABC University, 2018"
        ]
    },
    "Experience": {
        "Matched": [
        "Data Scientist",
        "Data Analyst"
        ],
        "Missing (JD)": [],
        "Extra (CV)": []
    }
    }

    model_id = "gemini-1.5-flash-latest"
    llm_agent = Agent(
        model=Gemini(id=model_id),
        description="You are an agent that generates recruiter-style questions based on CV and JD comparison.",
        instructions="Generate up to 8 recruiter-style clarification questions based on the provided CV, JD, and comparison data. Return ONLY a JSON list of strings.",
        show_tool_calls=False
    )
    agent = QnAAgent(llm_agent)
    questions = agent.generate_questions(cv_data, jd_data, comparison)
    print(questions)
