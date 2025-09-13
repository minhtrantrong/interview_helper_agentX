from typing import List
from agno.agent import Agent
from agno.models.google import Gemini

class CVJDQAAgent:
    """
    Advanced agent that analyzes a candidate's CV and a job description (JD), extracts and compares skills/experience, then generates categorized QA questions (technical, behavioral, situational) with reasoning to assess candidate level and fit.
    """
    def __init__(self, model_id: str = "gemini-1.5-flash-latest"):
        self.model = Gemini(id=model_id)
        self.agent = Agent(
            model=self.model,
            description="You are an expert interview agent. You analyze CVs and job descriptions, extract and compare skills, experience, and responsibilities, then generate categorized interview questions (technical, behavioral, situational) with reasoning to assess candidate level and fit.",
            instructions=(
                "Given a candidate's CV and a job description, do the following:\n"
                "1. Extract key skills, experience, and responsibilities from both CV and JD.\n"
                "2. Compare the CV and JD to identify matches, gaps, and unique strengths.\n"
                "3. Generate 3-5 technical, 2-3 behavioral, and 2-3 situational interview questions.\n"
                "4. For each question, provide a brief reasoning for why it is asked.\n"
                "5. Output the result in structured JSON with categories: 'technical', 'behavioral', 'situational', each containing questions and reasoning."
            ),
            show_tool_calls=False
        )

    def generate_questions(self, cv: str, jd: str) -> dict:
        prompt = (
            "Candidate CV:\n" + cv +
            "\n\nJob Description:\n" + jd +
            "\n\nFollow the instructions above and output only the structured JSON result."
        )
        response = self.agent.run(prompt)
        # Try to parse JSON output, fallback to raw string if parsing fails
        import json
        try:
            result = json.loads(response)
        except Exception:
            result = {"raw_output": response}
        return result

if __name__ == "__main__":
    # Example usage
    example_cv = (
        "John Doe\n"
        "5 years experience in Python, ML, and data engineering.\n"
        "Worked at Acme Corp as Senior Data Scientist.\n"
        "Led a team of 4, deployed ML models to cloud, mentored junior staff.\n"
        "Skills: Python, Machine Learning, Data Engineering, Cloud (AWS), Leadership, Mentoring."
    )
    example_jd = (
        "Looking for a Data Scientist with 3+ years experience in Python, ML, and cloud platforms.\n"
        "Should be able to lead projects, mentor juniors, and communicate with stakeholders.\n"
        "Skills required: Python, Machine Learning, Cloud (AWS/GCP), Project Leadership, Communication."
    )
    agent = CVJDQAAgent()
    result = agent.generate_questions(example_cv, example_jd)
    print("Generated Interview Questions (Structured):")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
