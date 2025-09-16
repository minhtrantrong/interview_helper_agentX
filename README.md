# 🤖 Agentic AI Chatbot with Streamlit and Gemini

This is an agentic AI chatbot application built using Streamlit. It features a conversational interface powered by the Google Gemini AI model, with a dedicated left panel for uploading and managing documents.

## ✨ Features

- **Interactive Chat Interface**: A real-time, conversational UI built with Streamlit's native chat components.
- **Agentic AI Integration**: Leverages the power of the **Gemini 2.5 Flash** model for fast and intelligent responses.
- **Document Upload**: Users can upload PDF document (`.pdf`) for the AI agent to reference (future implementation).
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
## SSL certificate
Has been downloaded from the TIDB 


## Configure database TIDB
database name: recruitment
SQL editor:

USE recruitment;
CREATE TABLE job_descriptions (
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
);

USE recruitment;

CREATE TABLE candidates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_id BIGINT NOT NULL,  -- liên kết tới job_descriptions
    name VARCHAR(255) NULL,
    email VARCHAR(255) NULL,
    phone VARCHAR(50) NULL,
    education JSON NULL,
    work_experience JSON NULL,
    skills JSON NULL,
    certifications JSON NULL,
    languages JSON NULL,
    cv_hash CHAR(64) NULL UNIQUE,  -- nếu muốn tracking CV trùng
    match_score DECIMAL(5,2) NULL, -- nếu dùng điểm đánh giá CV
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES job_descriptions(id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


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
## Upload your resume and job description in PDF format and chat with the AI agent

