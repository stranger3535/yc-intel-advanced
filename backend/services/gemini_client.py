# backend/services/gemini_client.py
import os
import google.generativeai as genai

def generate_answer(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "GEMINI_API_KEY is not set on the server."

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-1.5-pro")

    response = model.generate_content(prompt)

    return response.text
