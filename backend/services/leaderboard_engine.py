# backend/services/leaderboard_engine.py

from backend.db import get_db


def get_leaderboard_service():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT c.name, sc.momentum_score
        FROM company_scores sc
        JOIN companies c ON c.id = sc.company_id
        ORDER BY sc.momentum_score DESC
        LIMIT 10
    """)

    data = cur.fetchall()
    return data
