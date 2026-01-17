from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from backend.db import get_db


router = APIRouter()

@router.get("/{company_id}", tags=["Companies"])
def company_detail(company_id: int, db=Depends(get_db)):
    cur = db.cursor(cursor_factory=RealDictCursor)

    try:
        # ----------------------
        # Company
        # ----------------------
        cur.execute(
            "SELECT * FROM companies WHERE id = %s",
            (company_id,)
        )
        company = cur.fetchone()

        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # ----------------------
        # Snapshots (latest first)
        # ----------------------
        cur.execute("""
            SELECT *
            FROM company_snapshots
            WHERE company_id = %s
            ORDER BY scraped_at DESC
            LIMIT 50
        """, (company_id,))
        snapshots = cur.fetchall()

        # ----------------------
        # Changes (latest first)
        # ----------------------
        cur.execute("""
            SELECT *
            FROM company_changes
            WHERE company_id = %s
            ORDER BY detected_at DESC
            LIMIT 100
        """, (company_id,))
        changes = cur.fetchall()

        # ----------------------
        # Scores
        # ----------------------
        cur.execute("""
            SELECT *
            FROM company_scores
            WHERE company_id = %s
        """, (company_id,))
        scores = cur.fetchone()

        # ----------------------
        # Derived insights
        # ----------------------
        last_change = changes[0]["detected_at"] if changes else None

        return {
            "company": company,
            "snapshots": snapshots,
            "changes": changes,
            "scores": scores,
            "insights": {
                "total_changes": len(changes),
                "last_change_at": last_change
            }
        }

    finally:
        cur.close()
