from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from backend.db import engine

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str


@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest):
    q = req.question.lower().strip()

    if not q:
        raise HTTPException(status_code=400, detail="Empty question")

    # 1️⃣ Top fast-growing YC startups
    if "fast" in q and "growing" in q:
        sql = """
        SELECT name, momentum_score
        FROM companies
        ORDER BY momentum_score DESC
        LIMIT 5
        """
        rows = engine.execute(text(sql)).fetchall()
        return ChatResponse(
            answer="\n".join([f"{r[0]} (score {r[1]})" for r in rows])
        )

    # 2️⃣ Companies working on AI
    if "ai" in q:
        sql = """
        SELECT name, tags
        FROM companies
        WHERE tags ILIKE '%AI%'
        LIMIT 5
        """
        rows = engine.execute(text(sql)).fetchall()
        return ChatResponse(
            answer="\n".join([f"{r[0]} – {r[1]}" for r in rows])
        )

    # 3️⃣ Stage changes
    if "stage" in q:
        sql = """
        SELECT name, stage
        FROM companies
        ORDER BY updated_at DESC
        LIMIT 5
        """
        rows = engine.execute(text(sql)).fetchall()
        return ChatResponse(
            answer="\n".join([f"{r[0]} → {r[1]}" for r in rows])
        )

    # 4️⃣ Fallback
    return ChatResponse(
        answer=(
            "I can answer questions about:\n"
            "- Fast-growing YC startups\n"
            "- AI companies\n"
            "- Stage changes\n"
            "- YC trends\n\n"
            "Try one of the example questions above."
        )
    )
