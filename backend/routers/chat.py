from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.chat_engine import answer_question

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(req: ChatRequest):
    question = req.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    return answer_question(question)
