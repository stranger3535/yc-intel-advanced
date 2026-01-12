from fastapi import APIRouter, Depends
from psycopg2.extras import RealDictCursor
from backend.db import get_db
from fastapi import APIRouter
from services.trend_engine import get_trends_service

router = APIRouter()


@router.get("/trends")
def trends(db=Depends(get_db)):
    cur = db.cursor(cursor_factory=RealDictCursor)

    # ----------------------
    # Top growing tags
    # ----------------------
    cur.execute("""
        SELECT
            tag,
            COUNT(*) AS count
        FROM company_snapshots,
             LATERAL jsonb_array_elements_text(tags) AS tag
        GROUP BY tag
        ORDER BY count DESC
        LIMIT 10
    """)
    top_tags = cur.fetchall()

    # ----------------------
    # Top locations
    # ----------------------
    cur.execute("""
        SELECT
            location,
            COUNT(*) AS count
        FROM company_snapshots
        WHERE location IS NOT NULL AND location <> ''
        GROUP BY location
        ORDER BY count DESC
        LIMIT 10
    """)
    top_locations = cur.fetchall()

    # ----------------------
    # Stage / change trends
    # ----------------------
    cur.execute("""
        SELECT
            change_type,
            COUNT(*) AS count
        FROM company_changes
        GROUP BY change_type
        ORDER BY count DESC
    """)
    stage_transitions = cur.fetchall()

    cur.close()

    return {
        "top_tags": top_tags,
        "top_locations": top_locations,
        "stage_transitions": stage_transitions
    }
