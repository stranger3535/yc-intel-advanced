from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from backend.db import get_db

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("")
def leaderboard(db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    cur = db.cursor(cursor_factory=RealDictCursor)

    try:
        # Top momentum companies
        cur.execute("""
            SELECT c.name, s.momentum_score
            FROM company_scores s
            JOIN companies c ON c.id = s.company_id
            ORDER BY s.momentum_score DESC
            LIMIT 10
        """)
        top_momentum = cur.fetchall()

        # Most stable companies
        cur.execute("""
            SELECT c.name, s.stability_score
            FROM company_scores s
            JOIN companies c ON c.id = s.company_id
            ORDER BY s.stability_score DESC
            LIMIT 10
        """)
        most_stable = cur.fetchall()

        # Recent changes
        cur.execute("""
            SELECT c.name, ch.change_type, ch.detected_at
            FROM company_changes ch
            JOIN companies c ON c.id = ch.company_id
            ORDER BY ch.detected_at DESC
            LIMIT 10
        """)
        recent_changes = cur.fetchall()

        return {
            "top_momentum": top_momentum,
            "most_stable": most_stable,
            "recent_changes": recent_changes
        }

    finally:
        cur.close()
