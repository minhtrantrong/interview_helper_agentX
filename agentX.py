import streamlit as st
import time
# Import the new module from the agents directory
from agents.llm_gemini import get_gemini_response

# Set page configuration with a wide layout and a title.
st.set_page_config(layout="wide", page_title="AI Chatbot Agent", page_icon="🤖")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# --- Left Panel for Document Upload and Display ---
with st.sidebar:
    st.title("📁 Documents")
    st.markdown("Upload documents for the AI agent to reference.")

    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=["pdf", "docx", "txt", "csv"],
        key="file_uploader"
    )

    if uploaded_file and uploaded_file.name not in [f.name for f in st.session_state.uploaded_files]:
        st.session_state.uploaded_files.append(uploaded_file)
        st.toast(f"File **{uploaded_file.name}** uploaded successfully!", icon="✅")
        st.rerun()

    st.subheader("Uploaded Files")
    if st.session_state.uploaded_files:
        for uploaded_file in st.session_state.uploaded_files:
            st.markdown(f"- **{uploaded_file.name}**")
    else:
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
                # Call the new function from the llm_gemini module
                response = get_gemini_response(user_input)
                st.write(response)

            # Add assistant's response to history
            st.session_state.messages.append({"role": "assistant", "content": response, "avatar": "🤖"})
    st.rerun()