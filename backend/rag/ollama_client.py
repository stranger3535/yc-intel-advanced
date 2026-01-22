import os
import requests
from backend.prompts.system_prompt import YC_SYSTEM_PROMPT

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def generate_answer(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "system": YC_SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "top_p": 0.9
        }
    }

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=120
    )

    response.raise_for_status()
    return response.json()["response"]