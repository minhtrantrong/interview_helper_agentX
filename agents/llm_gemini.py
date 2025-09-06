import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# We create a custom LLM class that Agno/LangChain can use
class GeminiFlashLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "gemini-flash"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred: {e}"

    def _get_api_key(self) -> str:
        return GOOGLE_API_KEY

# This is the instance that you will import and use
llm = GeminiFlashLLM()