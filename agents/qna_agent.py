import os
import json
import re
from typing import Dict, List
from agno.agent import Agent
from agno.models.google import Gemini
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")


class QnAAgent(Agent):
    """An agent that generates recruiter-style Q&A based on CV and JD content."""

    description = "Generates recruiter-style interview questions grouped by skill and level."

    def __init__(self, **kwargs):
        super().__init__(model=Gemini(id="gemini-2.5-flash"), **kwargs)
        self.name = "QnA Agent"

    def execute(
        self,
        cv_content: str,
        jd_content: str,
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        Generate recruiter-style screening questions grouped by skill and level.
        - Level 1: Basic theory checks
        - Level 2: Practical/project validation
        - Level 3: Advanced/problem-solving/missing JD skills

        :param cv_content: Extracted CV content as plain text
        :param jd_content: Extracted JD content as plain text
        :return: Dict structured by skill → {Level 1, Level 2, Level 3}
        """
        prompt_template = PromptTemplate.from_template(
            """
            You are a recruiter preparing candidate screening questions.

            Candidate CV:
            {cv_content}

            Job Description (JD):
            {jd_content}

            Instructions:
            - Identify key skills from CV and JD.
            - For EACH relevant skill, generate 2–3 questions per level.
            - Structure output strictly in JSON format:

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
              Level 1 (Basic Theory): Simple concept checks.
              Level 2 (Practical Application): Real project usage.
              Level 3 (Advanced/Missing Skills): Complex challenges or missing JD skills.

            - Cover:
              * CV skills (L1+L2)
              * Missing JD skills (L3)
              * Extra CV skills (L2 or L3, if relevant)

            - Return ONLY valid JSON.
            """
        )

        formatted_prompt = prompt_template.format(
            cv_content=cv_content, jd_content=jd_content
        )

        response = self.run(formatted_prompt)
        raw = response.content if hasattr(response, "content") else str(response)

        cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

        try:
            questions = json.loads(cleaned)
            if not isinstance(questions, dict):
                raise ValueError("Expected JSON object grouped by skills")
        except Exception:
            questions = {
                "General": {
                    "Level 1": [],
                    "Level 2": [],
                    "Level 3": [cleaned],
                }
            }

        return questions
