# backend/services/chat_engine.py

from services.search_engine import search_companies_service
from services.trend_engine import get_trends_service
from services.leaderboard_engine import get_leaderboard_service


def answer_question(question: str):
    q = question.lower()

    if "top" in q or "momentum" in q:
        return {
            "intent": "leaderboard",
            "data": get_leaderboard_service()
        }

    if "trend" in q:
        return {
            "intent": "trends",
            "data": get_trends_service()
        }

    if "search" in q or "company" in q:
        return {
            "intent": "search",
            "data": search_companies_service(
                q.replace("search", "").strip(),
                limit=10,
                sort="relevance"
            )
        }

    return {
        "intent": "unknown",
        "message": "Ask about companies, trends, or rankings."
    }
