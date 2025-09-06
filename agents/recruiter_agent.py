import os
from agno.agent import Agent
from langchain.prompts import PromptTemplate
# from agents.llm_gemini import llm
from agno.models.google import Gemini
from agents.prompt import RECRUITER_PROMPT

from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

class RecruiterAgent(Agent):
    """An agent that acts as a recruiter to evaluate a resume against a job description."""
    
    name = "Recruiter Agent"
    description = "Evaluates a resume and compares it against a job description."
    
    def __init__(self, **kwargs):
        super().__init__(model=Gemini(id="gemini-2.5-flash"), **kwargs)
    
    def run_evaluation(self, resume_content: str, jd_content: str, user_request: str) -> str:
        """
        Runs the recruiter evaluation process.
        :param resume_content: The content of the user's resume.
        :param jd_content: The content of the job description.
        :param user_request: The user's specific request or question.
        :return: A detailed evaluation of the match.
        """
        prompt = PromptTemplate.from_template(RECRUITER_PROMPT)
        formatted_prompt = prompt.format(resume_content=resume_content, jd_content=jd_content)
        
        # Combine the prompt and user request
        full_query = f"{formatted_prompt}\n\nUser's Request: {user_request}"
        
        # The Agno Agent's `run` method is used to execute the query.
        response = self.run(full_query)
        return response