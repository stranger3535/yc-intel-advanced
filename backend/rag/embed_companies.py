import sys
import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ------------------ FIX IMPORT PATH ------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

from backend.db import get_db

# ------------------ CONFIG ------------------
INDEX_PATH = "backend/rag/vector_store.faiss"
META_PATH = "backend/rag/metadata.json"

model = SentenceTransformer("all-MiniLM-L6-v2")

def main():
    db = get_db()
    cur = db.cursor()

    # ✅ IMPORTANT: use ONLY latest snapshot per company
    cur.execute("""
        SELECT DISTINCT ON (c.id)
            c.id,
            c.name,
            cs.description,
            cs.location,
            cs.tags
        FROM companies c
        JOIN company_snapshots cs ON cs.company_id = c.id
        WHERE cs.description IS NOT NULL
        ORDER BY c.id, cs.scraped_at DESC
    """)

    rows = cur.fetchall()

    texts = []
    metadata = []

    for r in rows:
        text = f"""
Company: {r[1]}
Location: {r[3]}
Tags: {r[4]}
Description: {r[2]}
"""
        texts.append(text.strip())
        metadata.append({
            "company_id": r[0],
            "name": r[1]
        })

    print(f"Embedding {len(texts)} companies...")

    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    cur.close()
    db.close()

    print(f"✅ Embedded {len(texts)} companies successfully")

if __name__ == "__main__":
    main()
