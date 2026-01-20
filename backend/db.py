import os
import psycopg2
from fastapi import HTTPException
from dotenv import load_dotenv
from pathlib import Path

# --------------------------------------------------
# Explicitly load backend/.env
# --------------------------------------------------
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# --------------------------------------------------
# Read database URL
# --------------------------------------------------
DATABASE_URL = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")


def get_db():
    """
    FastAPI dependency that returns a PostgreSQL connection.
    """

    if not DATABASE_URL:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL not set. Database is required."
        )

    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {e}"
        )