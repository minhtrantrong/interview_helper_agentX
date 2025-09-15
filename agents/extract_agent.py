import os
import json
from agno.agent import Agent
from agno.tools import tool
from agno.models.google import Gemini
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print("GOOGLE_API_KEY", GOOGLE_API_KEY)

class ExtractionAgent(Agent):
    """Agent dùng để trích xuất thông tin chuẩn schema từ CV và JD."""

    description = "Extracts structured resume and job description data for database storage."

    def __init__(self, **kwargs):
        super().__init__(model=Gemini(id="gemini-2.5-flash"), **kwargs)
        self.name = "Extraction Agent"

    def extract_resume_fields(self, resume_content: str) -> dict:
        query = f"""
        Extract the following fields from the resume and return valid JSON strictly in this schema:
        {{
          "name": "string",
          "email": "string",
          "phone": "string",
          "education": [
            {{
              "degree": "string",
              "institution": "string",
              "year": "string"
            }}
          ],
          "work_experience": [
            {{
              "company": "string",
              "role": "string",
              "duration": "string",
              "achievements": "string"
            }}
          ],
          "skills": ["string"],
          "certifications": ["string"],
          "languages": ["string"]
        }}

        Resume:
        {resume_content}
        """
        response = self.run(query)
        raw_text = response.output if hasattr(response, "output") else str(response)

        try:
            return json.loads(raw_text)
        except Exception:
            return {"raw_response": raw_text}


    def extract_jd_fields(self, jd_content: str) -> dict:
        query = f"""
        Extract the following fields from the job description and return valid JSON strictly in this schema:
        {{
          "job_title": "string",
          "company": "string",
          "location": "string",
          "responsibilities": ["string"],
          "required_skills": ["string"],
          "preferred_skills": ["string"],
          "experience": {{
            "years": "string",
            "domain": "string"
          }},
          "education_requirement": "string",
          "salary": "string"
        }}

        Job Description:
        {jd_content}
        """
        response = self.run(query)
        raw_text = response.output if hasattr(response, "output") else str(response)

        try:
            return json.loads(raw_text)
        except Exception:
            return {"raw_response": raw_text}
    def execute(self, resume_content: str, jd_content: str) -> dict:
            """
            Run both resume and job description extraction, then print results.
            """
            resume_data = self.extract_resume_fields(resume_content)
            jd_data = self.extract_jd_fields(jd_content)

            print("\n===== Resume Extraction Result =====")
            print(json.dumps(resume_data, indent=2, ensure_ascii=False))

            print("\n===== Job Description Extraction Result =====")
            print(json.dumps(jd_data, indent=2, ensure_ascii=False))

            return {
                "resume": resume_data,
                "job_description": jd_data
            }