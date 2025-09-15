import os
import json
import re
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
from db.tidb_client import get_tidb_connection, insert_job_description, insert_candidate
from json_repair import repair_json

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print("GOOGLE_API_KEY", GOOGLE_API_KEY)


class ExtractionAgent(Agent):
    """Agent dùng để trích xuất thông tin chuẩn schema từ CV và JD."""

    description = "Extracts structured resume and job description data for database storage."

    def __init__(self, **kwargs):
        # 1 connection + cursor duy nhất
        self.conn = get_tidb_connection()
        self.cursor = self.conn.cursor()
        super().__init__(model=Gemini(id="gemini-2.5-flash"), **kwargs)
        self.name = "Extraction Agent"

    def safe_extract_json(self, raw_text: str) -> dict:
        """Parse JSON an toàn, kể cả khi model trả về có ```json ...``` hoặc JSON bị lỗi cú pháp."""
        # Nếu raw_text là đối tượng có thuộc tính 'content', lấy nó
        if hasattr(raw_text, 'content'):
            raw_text = raw_text.content

        raw_text = str(raw_text).strip()

        try:
            # 1. Tìm trong ```json ... ``` hoặc ``` ... ```
            match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw_text, re.DOTALL)
            if match:
                cleaned = match.group(1).strip()
            else:
                cleaned = raw_text

            # 👇 THỬ SỬA JSON TRƯỚC KHI PARSE
            try:
                repaired = repair_json(cleaned)
                return json.loads(repaired)
            except Exception as e:
                print("❌ Failed to repair JSON:", e)
                raise

        except json.JSONDecodeError as e:
            print("❌ JSON parse error:", e)
            print("⚠️ Raw text:", raw_text[:500], "..." if len(raw_text) > 500 else "")
            return {}
        except Exception as e:
            print("❌ Unexpected error:", e)
            return {}

        except json.JSONDecodeError as e:
            print("❌ JSON parse error:", e)
            print("⚠️ Raw text:", raw_text[:300], "..." if len(raw_text) > 300 else "")
            return {}
        except Exception as e:
            print("❌ Unexpected error:", e)
            return {}

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
        raw_text = response.content if hasattr(response, 'content') else str(response)
        return self.safe_extract_json(raw_text) or {"raw_response": raw_text}

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
        raw_text = response.content if hasattr(response, 'content') else str(response)

        return self.safe_extract_json(raw_text) or {"raw_response": raw_text}

    def execute(self, resume_content: str, jd_content: str) -> dict:
        """Extract và lưu dữ liệu vào DB."""
        try:
            resume_data = self.extract_resume_fields(resume_content)
            jd_data = self.extract_jd_fields(jd_content)

            # Lưu JD trước -> lấy job_id
            job_id = insert_job_description(self.cursor, jd_content, jd_data)

            # Lưu Candidate gắn với job_id
            insert_candidate(self.cursor, job_id, resume_data)

            # Commit sau cùng
            self.conn.commit()

            print("\n===== Resume Extraction Result =====")
            print(json.dumps(resume_data, indent=2, ensure_ascii=False))

            print("\n===== Job Description Extraction Result =====")
            print(json.dumps(jd_data, indent=2, ensure_ascii=False))

            return {
                "resume": resume_data,
                "job_description": jd_data,
                "job_id": job_id,
            }

        except Exception as e:
            self.conn.rollback()
            print("❌ Error in execute:", e)
            raise e
