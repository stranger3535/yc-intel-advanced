from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from backend.db import get_db

router = APIRouter(prefix="/api/trends", tags=["Trends"])


@router.get("")
def trends(db=Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    cur = db.cursor(cursor_factory=RealDictCursor)

    try:
        # 🔹 Trend = most common tags across companies
        cur.execute("""
            SELECT
                tag AS category,
                COUNT(*) AS count
            FROM company_snapshots,
                 LATERAL jsonb_array_elements_text(tags) AS tag
            GROUP BY tag
            ORDER BY count DESC
            LIMIT 20
        """)

        return cur.fetchall()   # ✅ RETURNS ARRAY

    finally:
        cur.close()
        db.close()