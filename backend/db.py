import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL / NEON_DATABASE_URL not set")


def get_db():
    """
    Returns a new PostgreSQL connection.
    Caller must close it.
    """
    return psycopg2.connect(DATABASE_URL)
