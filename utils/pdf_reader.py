import streamlit as st
import time
from agents.llm_gemini import get_gemini_response
from utils.pdf_reader import extract_text_from_pdf

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

    # Resume uploader
    uploaded_cv = st.file_uploader(
        "Choose your resume", 
        type=["pdf"],
        key="cv_uploader"
    )

    if uploaded_cv:
        # Check if a new file has been uploaded
        if st.session_state.uploaded_files["resume"]["name"] != uploaded_cv.name:
            st.session_state.uploaded_files["resume"]["name"] = uploaded_cv.name
            
            # Read the file content
            text_content = extract_text_from_pdf(uploaded_cv)
            st.session_state.uploaded_files["resume"]["content"] = text_content
            
            st.toast(f"Resume **{uploaded_cv.name}** uploaded successfully!", icon="✅")
            st.rerun()

    st.markdown("---")

    # Job Description uploader
    uploaded_jd = st.file_uploader(
        "Choose a job description",
        type=["pdf"],
        key="jd_uploader"
    )

    if uploaded_jd:
        # Check if a new file has been uploaded
        if st.session_state.uploaded_files["job_description"]["name"] != uploaded_jd.name:
            st.session_state.uploaded_files["job_description"]["name"] = uploaded_jd.name
            
            # Read the file content
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

# --- Text Input at the bottom ---
if user_input := st.chat_input("What do you need help with?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input, "avatar": "🧑‍💻"})

    # Display user message in chat container
    with chat_placeholder.container():
        with st.chat_message("user", avatar="🧑‍💻"):
            st.write(user_input)

        # Generate and display assistant's response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = get_gemini_response(user_input)
                st.write(response)

            # Add assistant's response to history
            st.session_state.messages.append({"role": "assistant", "content": response, "avatar": "🤖"})
    st.rerun()