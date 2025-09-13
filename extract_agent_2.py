import json
import re
from typing import Dict, Any, List
from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import numpy as np


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
import re
import json
from typing import Dict, Any, List

class CVJDExtractorAgent:
    """
    Agent to extract structured data from CV and Job Description (JD),
    using regex first (fast + deterministic) and falling back to LLM if needed.
    All extraction is done via extract_fields, which is used as input for other functions.
    """

    def __init__(self, model_id: str = "gemini-1.5-flash-latest"):
        self.model = Gemini(id=model_id)
        self.agent = Agent(
            model=self.model,
            description=(
                "You are an agent that extracts structured information "
                "from CVs and Job Descriptions, and compares them."
            ),
            instructions=(
                "Given a CV and a Job Description, extract skills, education, "
                "experience, qualifications, and responsibilities. "
                "Then compare the skills between CV and JD, "
                "and summarize matches, gaps, and extras."
            ),
            show_tool_calls=False
        )

    # ---------------------- DOMAIN & FIELD ANALYSIS ----------------------

    def detect_domain(self, text: str) -> str:
        """
        Detect job domain/industry from JD or CV using simple LLM classification.
        """
        prompt = f"""
        Identify the industry domain of the following job description or CV:
        {text}

        Choose one from: IT, Finance, Healthcare, Marketing, Education, Engineering, Sales, Other.
        Return only the domain as a single word.
        """
        result = self.agent.run(prompt)
        return getattr(result, "content", str(result)).strip()

    def analyze_jd_fields(self, jd_text: str, domain: str) -> List[str]:
        """
        Use LLM to analyze a JD (with domain context) and determine which fields 
        should be extracted for candidate comparison.
        """
        prompt = f"""
        The job belongs to the domain: {domain}.

        Analyze the following Job Description text and identify the main fields
        that should be extracted for candidate comparison, considering this domain.

        Return the result strictly as a JSON list of field names 
        (e.g., ["Skills", "Qualifications", "Responsibilities", "Education", "Experience"]).
        
        JD Text:
        {jd_text}
        """
        response = self.agent.run(prompt)
        result = getattr(response, "content", str(response))

        try:
            fields = json.loads(result)
            if isinstance(fields, list):
                return fields
        except Exception:
            pass

        # fallback mặc định
        return ["Skills", "Qualifications", "Responsibilities", "Education", "Experience"]

    # ---------------------- EXTRACTION ----------------------

    def _extract_pattern(self, text: str, pattern: str, group: int = 1) -> str:
        """
        Extract text using regex pattern.
        """
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            if isinstance(matches[0], tuple):
                return " ".join(
                    m[group].strip() for m in matches if len(m) > group and m[group].strip()
                )
            return " ".join(m.strip() for m in matches if m.strip())
        return ""

    def _extract_with_llm(self, text: str, doc_type: str, fields: List[str]) -> Dict[str, Any]:
        """
        Fallback extraction using LLM when regex fails.
        """
        prompt = (
            f"Extract the following fields from this {doc_type}: {fields}\n\n{text}\n\n"
            f"Return JSON strictly with keys: {fields}"
        )
        response = self.agent.run(prompt)
        try:
            return json.loads(response.content if hasattr(response, "content") else str(response))
        except Exception:
            return {}

    def extract_fields(
        self, 
        text: str, 
        doc_type: str, 
        fields: Dict[str, str] = None, 
        field_names: List[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured fields from a given document text.
        
        Args:
            text: Nội dung văn bản (CV hoặc JD)
            doc_type: "CV" hoặc "Job Description"
            fields: dict {field: regex_pattern}
            field_names: nếu chỉ muốn extract một subset các field
        """
        if fields is None:
            # default patterns
            if doc_type == "CV":
                fields = {
                    "Skills": r"Skills\s*\n([\s\S]*?)(?=\n[A-Z][a-zA-Z ]*\n|$)",
                    "Education": r"Education\s*\n([\s\S]*?)(?=\n[A-Z][a-zA-Z ]*\n|$)",
                    "Experience": r"(?:Experience|Work Experience|Professional Experience)\s*\n([\s\S]*?)(?=\n[A-Z][a-zA-Z ]*\n|$)"
                }
            elif doc_type == "Job Description":
                fields = {
                    "Skills": r"(?:Skills Required|Required Skills|Skills)\s*\n([\s\S]*?)(?=\n[A-Z][a-zA-Z ]*\n|$)",
                    "Qualifications": r"(?:Qualifications|Requirements)\s*\n([\s\S]*?)(?=\n[A-Z][a-zA-Z ]*\n|$)",
                    "Responsibilities": r"(?:Responsibilities|Duties)\s*\n([\s\S]*?)(?=\n[A-Z][a-zA-Z ]*\n|$)"
                }

        # nếu chỉ lấy một subset
        if field_names:
            fields = {k: v for k, v in fields.items() if k in field_names}

        # chạy extract
        data = {}
        for key, pattern in fields.items():
            data[key] = self._extract_pattern(text, pattern)

        # fallback qua LLM nếu regex fail hết
        if not any(data.values()):
            data = self._extract_with_llm(text, doc_type, list(fields.keys()))

        return data

    # ---------------------- COMPARISON ----------------------

    def compare_cv_jd(self, cv_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare skills between CV and JD using deterministic matching.
        """
        cv_skills = set(self._normalize_list(self._split_items(cv_data.get("Skills", ""))))
        jd_skills = set(self._normalize_list(self._split_items(jd_data.get("Skills", ""))))

        matched = cv_skills & jd_skills
        missing = jd_skills - cv_skills
        extra = cv_skills - jd_skills

        return {
            "Matched Skills": sorted(matched),
            "Missing Skills (JD)": sorted(missing),
            "Extra Skills (CV)": sorted(extra)
        }

    def compare_cv_jd_llm(
        self, 
        cv_data: Dict[str, Any], 
        jd_data: Dict[str, Any], 
        fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare CV and JD dynamically with LLM for richer alignment.
        Fields can be provided; defaults to common ones (Skills, Experience, Qualifications).
        """
        if fields is None:
            fields = ["Skills", "Experience", "Qualifications"]

        # Build dynamic instruction per field
        field_instructions = []
        for f in fields:
            field_instructions.append(f"""
            For {f}:
            - Matched {f}
            - Missing {f} (JD)
            - Extra {f} (CV)
            """)
        
        field_instruction_text = "\n".join(field_instructions)

        prompt = f"""
        Compare the following candidate CV data with the Job Description (JD).
        Focus only on the provided fields: {fields}.
        Extract matched items, missing items, and extra items.
        Return the result as structured JSON with keys per field.

        JSON schema example:
        {{
            "Skills": {{
                "Matched": [...],
                "Missing (JD)": [...],
                "Extra (CV)": [...]
            }},
            "Experience": {{
                "Matched": [...],
                "Missing (JD)": [...]
            }}
            ...
        }}

        CV Data:
        {cv_data}

        JD Data:
        {jd_data}

        {field_instruction_text}
        """

        result = self.agent.run(prompt)
        try:
            return json.loads(result.content if hasattr(result, "content") else str(result))
        except Exception:
            return {"raw_output": result.content if hasattr(result, "content") else str(result)}


    # ---------------------- HELPERS ----------------------

    def _split_items(self, items: str) -> List[str]:
        return [i.strip() for i in re.split(r"[;,\n]", items) if i.strip()]

    def _normalize_list(self, items: List[str]) -> List[str]:
        return [re.sub(r"[^a-z0-9+# ]", "", i.lower()).strip() for i in items]
    
    def clean_llm_comparison(self, llm_comparison: dict) -> dict:
        """
        Convert LLM raw_output (with markdown ```json ... ```) into clean JSON dict.
        """
        raw_output = llm_comparison.get("raw_output", "")
        
        # Remove markdown ```json ... ``` wrappers
        cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_output.strip(), flags=re.MULTILINE)
        
        try:
            parsed = json.loads(cleaned)
            return parsed
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            return {}

    def get_embedding(self, sentence: str):
        try:
            embedder = SentenceTransformer("all-MiniLM-L6-v2")
            embedding = embedder.encode(sentence)
            return embedding.tolist()  # chuyển numpy -> list float
        except Exception as e:
            print(f"Embedding error: {e}")
            return []

    def compute_match_score(
        self, 
        cv_data: Dict[str, Any], 
        jd_data: Dict[str, Any], 
        fields: List[str] = None
    ) -> float:
        """
        Tính cosine similarity giữa CV và JD dựa trên embedding của các field quan trọng.
        
        Args:
            cv_data: dict data đã extract từ CV
            jd_data: dict data đã extract từ JD
            fields: danh sách field để so sánh (mặc định ["Skills","Qualifications","Responsibilities"])
        
        Returns:
            float score (0-1): mức độ match giữa CV và JD
        """
        if fields is None:
            fields = ["Skills", "Qualifications", "Responsibilities"]

        # Ghép text từ các field
        cv_text = " ".join([cv_data.get(f, "") for f in fields if f in cv_data])
        jd_text = " ".join([jd_data.get(f, "") for f in fields if f in jd_data])

        # Lấy embedding
        cv_vec = np.array(self.get_embedding(cv_text))
        jd_vec = np.array(self.get_embedding(jd_text))

        if cv_vec.size == 0 or jd_vec.size == 0:
            return 0.0

        # Reshape về (1, dim)
        cv_vec = cv_vec.reshape(1, -1)
        jd_vec = jd_vec.reshape(1, -1)

        # Tính cosine similarity
        score = cosine_similarity(cv_vec, jd_vec)[0][0]
        return float(score)
if __name__ == "__main__":
    cv_text = """Skills
Python, SQL, Data Visualization, Machine Learning, Deep Learning, Tableau, TensorFlow, Data Analysis

Education
Master of Data Science, University of Toronto, 2020
Bachelor of Computer Science, ABC University, 2018

Experience
Data Scientist, FinTech Solutions Inc, 2020–2024
- Built predictive models for customer churn using Python and TensorFlow.
- Developed interactive dashboards with Tableau and SQL for business stakeholders.
- Collaborated with engineering team to deploy ML models into production.

Data Analyst, Retail Insights Ltd, 2018–2020
- Conducted sales forecasting using regression models.
- Automated reporting pipelines using SQL and Python.
- Presented analytical findings to marketing and operations teams.
"""
    jd_text = """Skills Required
Python, SQL, Machine Learning, Communication, Cloud Platforms (AWS or GCP), Data Engineering

Qualifications
Master’s degree in Computer Science, Data Science, or related field
3+ years of professional experience in data-focused roles

Responsibilities
- Design and implement scalable ML models for financial risk analysis.
- Work with cross-functional teams to translate business requirements into data-driven solutions.
- Maintain data pipelines and ensure high-quality data availability.
- Communicate findings and insights effectively to both technical and non-technical audiences.
"""

    agent = CVJDExtractorAgent()
    # Step 1: Detect domain from JD
    domain = agent.detect_domain(jd_text)
    print(f"Detected domain: {domain}")

    # Step 2: Analyze JD fields using LLM (optional, can guide extraction)
    jd_fields_list = agent.analyze_jd_fields(jd_text, domain)
    print(f"JD fields to extract: {jd_fields_list}")

    # Step 3: Extract CV and JD data using extract_fields
    cv_data = agent.extract_fields(cv_text, "CV", field_names=jd_fields_list)
    jd_data = agent.extract_fields(jd_text, "Job Description", field_names=jd_fields_list)

    print("CV Data:", json.dumps(cv_data, indent=2, ensure_ascii=False))
    print("JD Data:", json.dumps(jd_data, indent=2, ensure_ascii=False))

    # Step 4: Compare CV and JD
    comparison = agent.compare_cv_jd(cv_data, jd_data)
    print("Comparison:", json.dumps(comparison, indent=2, ensure_ascii=False))

    # Step 5
    comparison_llm = agent.compare_cv_jd_llm(cv_data, jd_data, fields=jd_fields_list)
    print("Comparison (LLM):", json.dumps(comparison_llm, indent=2, ensure_ascii=False))

    # Step 6
    compute_match_score = agent.compute_match_score(cv_data, jd_data, fields=jd_fields_list)
    print("Match Score:", compute_match_score)

    # Step 7
    clean_llm_comparison = agent.clean_llm_comparison(comparison_llm)
    print("Comparison (LLM - Cleaned):", json.dumps(clean_llm_comparison, indent=2, ensure_ascii=False))