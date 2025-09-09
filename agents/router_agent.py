# agents/router_agent.py
import os
from agno.agent import Agent
from typing import List, Any
import json
from agno.tools import tool 
# from agno.models.google import Gemini
from agents.prompt import ROUTER_PROMPT
from agno.models.response import ModelResponse
from pydantic import BaseModel, Field
from agno.utils.log import logger
from agents.llm_gemini import llm
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

class RouterAgent(Agent):
    name = "Router Agent"
    description = "Routes user queries to the appropriate agent based on the user's intent."
    
    def __init__(self, 
                 recruiter_agent: Agent, 
                 knowledge_agent: Agent, 
                 resume_content: str, 
                 jd_content: str, 
                 user_request: str, 
                 **kwargs):
        self.recruiter_agent = recruiter_agent
        self.knowledge_agent = knowledge_agent
        self.user_request = user_request
        self.resume_content = resume_content
        self.jd_content = jd_content
        self.response = None
        # Correctly create a list of Agno-compatible tools from the agents
        def recruiter_agent_tool(self):
            return self.recruiter_agent.execute(self.resume_content, 
                                                self.jd_content, 
                                                self.user_request)
        def knowledge_agent_tool(self):
            return self.knowledge_agent.execute(self.resume_content, 
                                                self.jd_content, 
                                                self.user_request)
        
        tools = [recruiter_agent_tool, knowledge_agent_tool]
        
        super().__init__(
            model=llm,
            tools=tools, 
            instructions=[ROUTER_PROMPT],
            show_tool_calls=True,
            **kwargs
        )

    def execute(self) -> ModelResponse:
        # full_query = f"{ROUTER_PROMPT}\n\nUser's Request: {self.user_request}"
        full_query = f"User's Request: {self.user_request}"
        return self.run(full_query)