
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def get_llm_response(prompt, system_prompt=""):

    provider = os.getenv("LLM_PROVIDER", "gemini")

    if provider == "gemini":

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing in .env")

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            contents=prompt,
            config={
                "system_instruction": system_prompt,
                "temperature": 0.2,
                "max_output_tokens": 500
            }
        )

        return response.text

    else:
        raise ValueError("Unsupported LLM provider")
