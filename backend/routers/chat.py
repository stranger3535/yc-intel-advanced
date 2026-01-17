from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from rag.rag_pipeline import answer_question

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest):
    question = req.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    answer = answer_question(question)

    return {
        "answer": answer
    }
