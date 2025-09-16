# 🤖 Agentic AI Chatbot with Streamlit and Gemini

This is an agentic AI chatbot application built using Streamlit. It features a conversational interface powered by the Google Gemini AI model, with a dedicated left panel for uploading and managing documents.

## ✨ Features

- **Interactive Chat Interface**: A real-time, conversational UI built with Streamlit's native chat components.
- **Agentic AI Integration**: Leverages the power of the **Gemini 2.5 Flash** model for fast and intelligent responses.
- **Document Upload**: Users can upload various document types (`.pdf`, `.docx`, `.txt`, `.csv`) for the AI agent to reference (future implementation).
- **Secure API Key Management**: Uses a `.env` file to securely store and load the Google Gemini API key.
- **Clean UI**: A two-panel layout with a sidebar for document management and a main area for the chat conversation.

## ⚙️ Setup and Installation

Follow these steps to get the application up and running on your local machine.

## 1. Clone the repository

#### bash
`git clone git@github.com:minhtrantrong/interview_helper_agentX.git`
`cd your-repo-name`

## Create a virtual environment
`python -m venv venv`


## Activate the virtual environment
### On Windows:
`.\venv\Scripts\activate`
### On macOS/Linux:
`source venv/bin/activate`

## Install the required packages
`pip install -r requirements.txt`

## Configure database TIDB
database name: recruitment
SQL editor:
`CREATE TABLE candidates (
    id BIGINT(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    job_id BIGINT(20),
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    education JSON,
    work_experience JSON,
    skills JSON,
    certifications JSON,
    languages JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    match_score INT(11)
);`

`CREATE TABLE job_descriptions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(255) NULL,
    company VARCHAR(255) NULL,
    location VARCHAR(255) NULL,
    responsibilities JSON NULL,
    required_skills JSON NULL,
    preferred_skills JSON NULL,
    experience JSON NULL,
    education_requirement VARCHAR(255) NULL,
    salary VARCHAR(100) NULL,
    jd_hash CHAR(64) NULL UNIQUE, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);`

## Configure your API Key
The application requires a Google Gemini API key to function.

Get an API key from Google AI Studio.

Create a new file named .env in the root directory of the project.

Add your API key to this file in the following format:

GEMINI_API_KEY="YOUR_API_KEY_HERE"
Make sure to replace YOUR_API_KEY_HERE with your actual key.
## Run the application
Once the setup is complete, you can start the Streamlit application.
    `streamlit run agentX.py`

