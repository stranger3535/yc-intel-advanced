# backend/services/gemini_client.py
import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_answer(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "LLM is disabled. Please configure GEMINI_API_KEY."

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)
    return response.text
