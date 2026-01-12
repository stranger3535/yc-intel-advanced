import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()  # loads DATABASE_URL

DATABASE_URL = os.getenv("DATABASE_URL")

def main():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set in .env")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Simple health check: how many companies
    cur.execute("SELECT COUNT(*) AS count FROM companies;")
    row = cur.fetchone()
    print(f"companies table row count: {row['count']}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
