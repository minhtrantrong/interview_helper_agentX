import streamlit as st
import time
from utils.pdf_reader import extract_text_from_pdf
from agents.llm_gemini import llm
from agents.resume_reviewer import ResumeReviewerAgent
from agents.recruiter_agent import RecruiterAgent
from agents.router_agent import RouterAgent 
from agents.knowledge_agent import KnowledgeAgent
from agents.prompt import CHATBOT_PROMPT, ROUTER_PROMPT, TOOLS_PROMPT
from agno.team import Team
from agno.agent import Agent
from agno.models.google import Gemini
from langchain.prompts import PromptTemplate
from agno.tools import tool
from agents.qna_agent import QnAAgent


from dotenv import load_dotenv
load_dotenv()

# Set page configuration with a wide layout and a title.
st.set_page_config(layout="wide", page_title="AI Chatbot Agent", page_icon="🤖")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {
        "resume": {"name": None, "content": None},
        "job_description": {"name": None, "content": None}
    }

# --- Left Panel for Document Upload and Display ---
with st.sidebar:
    st.title("📁 Documents")
    st.markdown("Upload your Resume and Job Description here.")
    st.markdown("---")

    uploaded_cv = st.file_uploader(
        "Choose your resume", 
        type=["pdf"],
        key="cv_uploader"
    )

    if uploaded_cv:
        if st.session_state.uploaded_files["resume"]["name"] != uploaded_cv.name:
            st.session_state.uploaded_files["resume"]["name"] = uploaded_cv.name
            text_content = extract_text_from_pdf(uploaded_cv)
            st.session_state.uploaded_files["resume"]["content"] = text_content
            st.toast(f"Resume **{uploaded_cv.name}** uploaded successfully!", icon="✅")
            st.rerun()

    st.markdown("---")

    uploaded_jd = st.file_uploader(
        "Choose a job description",
        type=["pdf"],
        key="jd_uploader"
    )

    if uploaded_jd:
        if st.session_state.uploaded_files["job_description"]["name"] != uploaded_jd.name:
            st.session_state.uploaded_files["job_description"]["name"] = uploaded_jd.name
            text_content = extract_text_from_pdf(uploaded_jd)
            st.session_state.uploaded_files["job_description"]["content"] = text_content
            st.toast(f"Job Description **{uploaded_jd.name}** uploaded successfully!", icon="✅")
            st.rerun()
            
    st.subheader("Uploaded Files")
    if st.session_state.uploaded_files["resume"]["name"]:
        st.markdown(f"- **Resume:** `{st.session_state.uploaded_files['resume']['name']}`")
    if st.session_state.uploaded_files["job_description"]["name"]:
        st.markdown(f"- **Job Description:** `{st.session_state.uploaded_files['job_description']['name']}`")
    
    if not st.session_state.uploaded_files["resume"]["name"] and not st.session_state.uploaded_files["job_description"]["name"]:
        st.markdown("No documents uploaded yet.")

# --- Main Content Area: Chatbot Interface ---
st.title("🤖 Agentic AI Chatbot")

# --- Conversation History Container ---
chat_placeholder = st.empty()

with chat_placeholder.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.write(message["content"])
# Define agents and team:
recruiter_agent = RecruiterAgent()
knowledge_agent = KnowledgeAgent()
qna_agent = QnAAgent()
router_team = Team(
    name="Career Services Team",
    mode="route", # The Team will act as a router
    model=llm, # The routing logic will be powered by your Gemini LLM
    members=[recruiter_agent, knowledge_agent],
    markdown=True,
)

# --- Text Input at the bottom ---
if user_input := st.chat_input("What do you need help with?"):
    st.session_state.messages.append({"role": "user", "content": user_input, "avatar": "🧑‍💻"})

    with chat_placeholder.container():
        with st.chat_message("user", avatar="🧑‍💻"):
            st.write(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                resume_content = st.session_state.uploaded_files["resume"]["content"]
                jd_content = st.session_state.uploaded_files["job_description"]["content"]
                
                if resume_content and jd_content:
                    print("Team router working ...")
                    # agents=[recruiter_agent, knowledge_agent]
                    # router_agent = RouterAgent(agents, resume_content, jd_content, user_input)
                    
                    # router_agent = RouterAgent(recruiter_agent, 
                    #                            knowledge_agent, 
                    #                            resume_content, 
                    #                            jd_content, 
                    #                            user_input)
                    # router_response = router_agent.execute()
                    # def recruiter_agent_tool(resume_content, jd_content, user_input):
                    #     return recruiter_agent.execute(resume_content, jd_content, user_input)
                    # def knowledge_agent_tool(resume_content, jd_content, user_input):
                    #     return knowledge_agent.execute(resume_content, jd_content, user_input)
                    @tool
                    def recruiter_agent_tool() -> str:
                        """
                        Use this tool when the user is asking for feedback, review, or improvement 
                        suggestions on their resume in relation to a job description. 
                        Example queries: 
                        - "Can you review my resume?" 
                        - "What do recruiters think about my CV for this role?" 
                        - "How can I improve my resume for this internship?"
                        """
                        return recruiter_agent.execute(resume_content, jd_content, user_input)

                    @tool
                    def knowledge_agent_tool() -> str:
                        """
                        Use this tool when the user is asking about skill or knowledge gaps based on 
                        their resume and the job description, or seeking guidance on how to learn new skills. 
                        Example queries:
                        - "What skills am I missing for this job?" 
                        - "Which technologies should I study to match this role?" 
                        - "How can I improve my knowledge for the requirements listed?"
                        """
                        return knowledge_agent.execute(resume_content, jd_content, user_input)
                    
                    @tool
                    def qna_agent_tool() -> dict:
                        """
                        Use the QnA Agent to generate recruiter-style interview questions.
                        - Input: CV data, JD data
                        - Output: Dict grouped by skill → {Level 1, Level 2, Level 3}
                        """
                        return qna_agent.execute(resume_content, jd_content)
                                        
                    prompt = PromptTemplate.from_template(TOOLS_PROMPT)
                    formatted_prompt = prompt.format(resume_content=resume_content, 
                                                     jd_content=jd_content, 
                                                     user_input=user_input)
                    router = Agent(
                        model=Gemini(id="gemini-2.5-flash"),
                        tools = [recruiter_agent_tool, knowledge_agent_tool, qna_agent_tool],
                        instructions=formatted_prompt,
                        show_tool_calls=True,
                    )
                    router_response = router.run(f"user input: {user_input}")
                    # router_response = router_team.run(user_input)
                    # print(router_response)
                    response = router_response.content

                elif resume_content:
                    print("Review agent working ...")
                    resume_reviewer_agent = ResumeReviewerAgent()
                    run_response = resume_reviewer_agent.execute(
                        resume_content=resume_content,
                        user_request=user_input
                    )
                    response = run_response.content

                else:
                    print("Chatbot agent working ...")
                    full_query = CHATBOT_PROMPT + "\n\nUser's request: " + user_input
                    response = llm._call(full_query)
                
                st.write(response)

            st.session_state.messages.append({"role": "assistant", "content": response, "avatar": "🤖"})
    st.rerun()