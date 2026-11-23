import logging
import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

def get_llm_response(prompt, system_prompt=""):
    provider = os.getenv("LLM_PROVIDER", "gemini")

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing in .env")

        client = genai.Client(api_key=api_key)

        start_time = time.perf_counter()

        try:
            response = client.models.generate_content(
                model=os.getenv(
                    "GEMINI_MODEL",
                    "gemini-3.5-flash-lite"
                ),
                contents=prompt,
                config={
                    "system_instruction": system_prompt,
                    "temperature": 0.7,
                    "max_output_tokens": 500
                }
            )

            latency = time.perf_counter() - start_time
            usage = response.usage_metadata

            input_tokens = (
                usage.prompt_token_count if usage else None
            )
            output_tokens = (
                usage.candidates_token_count if usage else None
            )
            total_tokens = (
                usage.total_token_count if usage else None
            )

            logger.info(
                "LLM request | latency=%.2fs | "
                "input_tokens=%s | output_tokens=%s | "
                "total_tokens=%s",
                latency,
                input_tokens,
                output_tokens,
                total_tokens
            )

            return response.text

        except Exception:
            latency = time.perf_counter() - start_time

            logger.exception(
                "LLM request failed | latency=%.2fs",
                latency
            )
            raise

    else:
        raise ValueError("Unsupported LLM provider")