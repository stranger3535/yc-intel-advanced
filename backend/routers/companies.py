from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from backend.db import get_db

router = APIRouter(
    prefix="/api/companies",
    tags=["Companies"]
)

# =========================
# LIST COMPANIES
# =========================
@router.get("")
def list_companies(db=Depends(get_db)):
    cur = db.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                id,
                name,
                slug,
                domain,
                founded_year,
                is_active
            FROM companies
            ORDER BY name
            LIMIT 200
        """)
        return cur.fetchall()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        db.close()


# =========================
# COMPANY DETAIL
# =========================
@router.get("/{company_id}")
def company_detail(company_id: int, db=Depends(get_db)):
    cur = db.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute(
            "SELECT * FROM companies WHERE id = %s",
            (company_id,)
        )
        company = cur.fetchone()

        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        return company

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        db.close()