import os
from agno.agent import Agent
from langchain.prompts import PromptTemplate
# from agents.llm_gemini import llm
from agno.models.google import Gemini
from agents.prompt import KNOWLEDGE_CHECKER_PROMPT

from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

class KnowledgeAgent(Agent):
    """An agent that identifies skill gaps and suggests learning paths."""
    
    # name: str = "Knowledge Agent"
    description = "Analyzes job descriptions and resumes to identify lacking skills and provides guidance on gaining those skills."
    
    def __init__(self, **kwargs):
        # We pass your custom llm instance to the agent
        super().__init__(model=Gemini(id="gemini-2.5-flash"), **kwargs)
        self.name = "Knowledge Agent"
        
    def execute(self, resume_content: str, jd_content: str, user_request: str) -> str:
        """
        Compares a resume to a job description to find missing skills and
        suggests ways to acquire them.
        :param resume_content: The content of the user's resume.
        :param jd_content: The content of the job description.
        :return: A detailed report on skill gaps and a learning plan.
        """
        prompt = PromptTemplate.from_template(KNOWLEDGE_CHECKER_PROMPT)
        formatted_prompt = prompt.format(resume_content=resume_content, jd_content=jd_content)
        full_query = f"{formatted_prompt}\n\nUser's Request: {user_request}"
        # Agno's `run` method executes the prompt and returns the agent's response.
        response = self.run(full_query)
        return response