import os
from dotenv import load_dotenv
from groq import Groq
from google import genai

load_dotenv()


def get_llm_response(prompt, system_prompt=""):
    provider = os.getenv("LLM_PROVIDER", "groq")

    if provider == "groq":
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    elif provider == "gemini":
        client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config={
                "system_instruction": system_prompt
            }
        )

        return response.text

    else:
        raise ValueError("Unsupported LLM provider")