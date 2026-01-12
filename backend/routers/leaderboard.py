from fastapi import APIRouter, Depends
from psycopg2.extras import RealDictCursor
from db import get_db

router = APIRouter()

@router.get("/", tags=["Leaderboard"])
def leaderboard(db=Depends(get_db)):
    cur = db.cursor(cursor_factory=RealDictCursor)

    try:
        # --- Top momentum companies ---
        cur.execute("""
            SELECT
                c.id,
                c.name,
                sc.momentum_score
            FROM company_scores sc
            JOIN companies c ON c.id = sc.company_id
            ORDER BY sc.momentum_score DESC
            LIMIT 10
        """)
        top_momentum = cur.fetchall()

        # --- Most stable companies ---
        cur.execute("""
            SELECT
                c.id,
                c.name,
                sc.stability_score
            FROM company_scores sc
            JOIN companies c ON c.id = sc.company_id
            ORDER BY sc.stability_score DESC
            LIMIT 10
        """)
        top_stable = cur.fetchall()

        # --- Recently changed companies ---
        cur.execute("""
            SELECT
                c.id,
                c.name,
                MAX(cc.detected_at) AS last_change
            FROM company_changes cc
            JOIN companies c ON c.id = cc.company_id
            GROUP BY c.id, c.name
            ORDER BY last_change DESC
            LIMIT 10
        """)
        recent_changes = cur.fetchall()

        return {
            "top_momentum": top_momentum,
            "top_stable": top_stable,
            "recent_changes": recent_changes
        }

    finally:
        cur.close()
