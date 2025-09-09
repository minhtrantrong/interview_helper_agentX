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

# class RouterAgent(Agent):
#     name = "Router Agent"
#     description = "Routes user queries to the appropriate agent based on the user's intent."
    
#     def __init__(self, agents: List[Agent], **kwargs):
#         self.available_agents = {str(agent.name).replace(" ", "_").lower(): agent for agent in agents}
        
#         # Correctly create a list of Agno-compatible tools from the agents
#         tools=[self.route_to_knowledge_agent, self.route_to_recruiter_agent]
        
#         super().__init__(
#             model=Gemini(id="gemini-2.5-flash"),
#             tools=tools, # Pass the correctly formatted tools here
#             instructions=[ROUTER_PROMPT],
#             **kwargs
#         )
#     @tool(
#         name="knowledge_agent_router",
#         description="Routes user queries to the Knowledge Agent for skill gap analysis and learning guidance.",
#     )
#     def route_to_knowledge_agent(self, message: str) -> str:
#         """
#         Routes the message to the Knowledge Agent.
#         :param message: The user's original message.
#         """
#         # This function will be called by the LLM. In a real application,
#         # you would call the KnowledgeAgent's method here.
#         return f"Query has been routed to the Knowledge Agent."

#     @tool(
#         name="recruiter_agent_router",
#         description="Routes user queries to the Recruiter Agent for resume feedback and job description evaluation.",
#     )
#     def route_to_recruiter_agent(self, message: str) -> str:
#         """
#         Routes the message to the Recruiter Agent.
#         :param message: The user's original message.
#         """
#         # This function will be called by the LLM.
#         return f"Query has been routed to the Recruiter Agent."

#     def run_router(self, user_message: str):
#         return self.run(user_message)

class RouterAgent(Agent):
    name = "Router Agent"
    description = "Routes user queries to the appropriate agent based on the user's intent."
    
    def __init__(self, agents: List[Agent], 
                 resume_content: str, 
                 jd_content: str, 
                 user_request: str, 
                 **kwargs):
        self.available_agents = {str(agent.name).replace(" ", "_").lower(): agent for agent in agents}
        self.user_request = user_request
        self.resume_content = resume_content
        self.jd_content = jd_content
        self.response = None
        # Correctly create a list of Agno-compatible tools from the agents
        tools = [self._create_tool_for_agent(agent) for agent in agents]
        
        super().__init__(
            model=llm,
            tools=tools, 
            instructions=[ROUTER_PROMPT],
            **kwargs
        )
        
    def _create_tool_for_agent(self, agent: Agent):
        agent_name = str(agent.name).replace(" ", "_").lower()
        tool_desc = f"Use this tool to route a message to the {agent.name}."
        
        # Define the Pydantic model for the tool's parameters
        class RouteParams(BaseModel):
            message: str = Field(..., description="The user's original message to be passed to the agent.")
        
        # The tool's function needs to be a proper callable that the model can invoke.
        # This function will handle the routing logic.
        def route_to_agent_tool(agent_name) :
            self.response = self.available_agents[agent_name].execute(self.resume_content, 
                                                                      self.jd_content, 
                                                                      self.user_request)
            logger.info(f"Route to {agent_name} successful with response: {self.response}")
            return self.response
        

        return tool(
            name=agent_name,
            description=tool_desc,
        )(route_to_agent_tool)

    def execute(self) -> ModelResponse:
        # full_query = f"{ROUTER_PROMPT}\n\nUser's Request: {self.user_request}"
        full_query = f"{ROUTER_PROMPT}\n\nUser's Request: {self.user_request}"
        # response_content = self.run(full_query)

        # We now have the content from the executed agent.
        return self.run(full_query)