import logging
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


class LLMProviderError(RuntimeError):
    status_code = 502
    public_message = (
        "The language model rejected the request. Check GEMINI_API_KEY "
        "and GEMINI_MODEL."
    )


class LLMUnavailableError(LLMProviderError):
    status_code = 503
    public_message = (
        "The language model is temporarily unavailable. Please try again."
    )


def get_llm_response(prompt, system_prompt=""):
    provider = os.getenv("LLM_PROVIDER", "gemini")

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise LLMProviderError("GEMINI_API_KEY is missing.")

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30_000,
                retry_options=types.HttpRetryOptions(
                    attempts=2,
                    initial_delay=1,
                    max_delay=2,
                    exp_base=2,
                    jitter=0.1,
                    http_status_codes=[408, 429, 500, 502, 503, 504]
                )
            )
        )

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

        except APIError as error:
            latency = time.perf_counter() - start_time

            logger.exception(
                "LLM request failed | status=%s | latency=%.2fs",
                error.code,
                latency
            )

            if error.code in (408, 429) or error.code >= 500:
                raise LLMUnavailableError() from error

            raise LLMProviderError() from error

        except Exception:
            latency = time.perf_counter() - start_time

            logger.exception(
                "LLM request failed | latency=%.2fs",
                latency
            )
            raise

    else:
        raise LLMProviderError("Unsupported LLM provider.")