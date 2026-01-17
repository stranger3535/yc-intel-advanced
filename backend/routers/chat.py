from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import google.generativeai as genai

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "answer": "Gemini API key is not configured on the server."
        }

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        response = model.generate_content(question)
        return {
            "answer": response.text or "No response generated."
        }
    except Exception as e:
        return {
            "answer": f"Gemini error: {str(e)}"
        }
