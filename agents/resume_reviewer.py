import os
from agno.agent import Agent
from langchain.prompts import PromptTemplate
# from agents.llm_gemini import llm
from agno.models.google import Gemini
from agents.prompt import RESUME_REVIEWER_PROMPT

from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

class ResumeReviewerAgent(Agent):
    """An agent that reviews a resume and provides professional feedback."""
    
    name = "Resume Reviewer Agent"
    description = "Provides professional and constructive feedback on a resume."
    
    def __init__(self, **kwargs):
        super().__init__(model=Gemini(id="gemini-2.5-flash"), **kwargs)
    
    def run_review(self, resume_content: str, user_request: str) -> str:
        """
        Runs the resume review process.
        :param resume_content: The content of the user's resume.
        :param user_request: The user's specific request or question.
        :return: A detailed review of the resume.
        """
        prompt = PromptTemplate.from_template(RESUME_REVIEWER_PROMPT)
        formatted_prompt = prompt.format(resume_content=resume_content)
        
        # Combine the prompt and user request
        full_query = f"{formatted_prompt}\n\nUser's Request: {user_request}"
        
        # The Agno Agent's `run` method is used to execute the query.
        response = self.run(full_query)
        return response