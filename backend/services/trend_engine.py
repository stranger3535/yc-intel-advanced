from backend.db import get_db

def get_trends_service():
    conn = get_db()
    cur = conn.cursor()

    # Top tags
    cur.execute("""
        SELECT tag, COUNT(*) AS count
        FROM company_snapshots,
        jsonb_array_elements_text(tags) AS tag
        GROUP BY tag
        ORDER BY count DESC
        LIMIT 10
    """)
    tags = cur.fetchall()

    # Top locations
    cur.execute("""
        SELECT location, COUNT(*)
        FROM company_snapshots
        GROUP BY location
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    locations = cur.fetchall()

    # Change types
    cur.execute("""
        SELECT change_type, COUNT(*)
        FROM company_changes
        GROUP BY change_type
    """)
    changes = cur.fetchall()

    return {
        "top_tags": tags,
        "top_locations": locations,
        "stage_transitions": changes
    }
