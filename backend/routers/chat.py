from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str  # MUST be string

@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest):
    question = req.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # LLM disabled (free tier safe mode)
    if not os.getenv("GEMINI_API_KEY"):
        return ChatResponse(
            answer=(
                "LLM is currently disabled.\n\n"
                "This demo runs on Render free tier without Gemini enabled.\n"
                "You can still explore YC data via search, trends, and leaderboards."
            )
        )

    # Placeholder for future Gemini logic
    return ChatResponse(
        answer="Gemini is enabled, but response logic is not implemented yet."
    )
