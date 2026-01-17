from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

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


    # (Render cannot run Ollama anyway)
    if not os.getenv("OLLAMA_ENABLED"):
        return ChatResponse(
            answer=(
                "LLM is disabled on the deployed server.\n\n"
                "This project demonstrates:\n"
                "- YC data APIs\n"
                "- Chat interface\n"
                "- Deployment architecture\n\n"
                "LLM responses work locally with Ollama."
            )
        )

    # (This part will ONLY work locally, not on Render)
    try:
        # placeholder for your local ollama call
        return ChatResponse(answer="Ollama response placeholder")
    except Exception as e:
        return ChatResponse(answer=f"Error: {str(e)}")
