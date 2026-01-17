from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.rag.rag_pipeline import answer_question

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: list = []   # optional but future-proof

@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest):
    question = req.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = answer_question(question)

 
    if isinstance(result, dict):
        return {
            "answer": result.get("answer", "No answer available."),
            "sources": result.get("sources", [])
        }

    # If result is plain string
    return {
        "answer": str(result),
        "sources": []
    }
