from fastapi import APIRouter, Depends, Query
from psycopg2.extras import RealDictCursor
from backend.db import get_db

router = APIRouter()

@router.get("/search", tags=["Search"])
def search_companies(
    q: str = Query(..., min_length=2, description="Search keywords"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    sort: str = Query("relevance", regex="^(relevance|momentum)$"),
    db=Depends(get_db)
):
    offset = (page - 1) * limit
    cur = db.cursor(cursor_factory=RealDictCursor)

    order_clause = (
        "ts_rank(cs.search_vector, plainto_tsquery('english', %s)) DESC"
        if sort == "relevance"
        else "sc.momentum_score DESC NULLS LAST"
    )

    sql = f"""
        WITH latest_snapshot AS (
            SELECT DISTINCT ON (company_id)
                company_id,
                search_vector
            FROM company_snapshots
            ORDER BY company_id, scraped_at DESC
        )
        SELECT
            c.id,
            c.name,
            c.domain,
            sc.momentum_score
        FROM companies c
        JOIN latest_snapshot cs ON cs.company_id = c.id
        LEFT JOIN company_scores sc ON sc.company_id = c.id
        WHERE cs.search_vector @@ plainto_tsquery('english', %s)
        ORDER BY {order_clause}
        LIMIT %s OFFSET %s
    """

    try:
        cur.execute(sql, (q, q, limit, offset))
        results = cur.fetchall()

        return {
            "query": q,
            "page": page,
            "limit": limit,
            "count": len(results),
            "results": results
        }

    finally:
        cur.close()
