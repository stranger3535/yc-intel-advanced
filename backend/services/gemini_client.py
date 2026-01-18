import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_answer(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY is not configured"

    genai.configure(api_key=GEMINI_API_KEY)

    # ✅ USE A SUPPORTED MODEL
    model = genai.GenerativeModel("gemini-1.5-pro")

    response = model.generate_content(prompt)
    return response.text
