from backend.db import get_db

def search_companies_service(q: str, limit: int, sort: str):
    conn = get_db()
    cur = conn.cursor()

    order_by = """
        ts_rank(cs.search_vector, plainto_tsquery(%s)) DESC
    """ if sort == "relevance" else "sc.momentum_score DESC"

    query = f"""
        SELECT
            c.id,
            c.name,
            COALESCE(sc.momentum_score, 0) AS momentum
        FROM companies c
        JOIN company_snapshots cs
            ON cs.company_id = c.id
        LEFT JOIN company_scores sc
            ON sc.company_id = c.id
        WHERE cs.search_vector @@ plainto_tsquery(%s)
        ORDER BY {order_by}
        LIMIT %s
    """

    cur.execute(query, (q, q, limit))
    rows = cur.fetchall()

    return [
        {
            "id": r[0],
            "name": r[1],
            "momentum_score": r[2]
        }
        for r in rows
    ]
