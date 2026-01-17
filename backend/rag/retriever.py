# backend/rag/retriever.py
import os

FAISS_ENABLED = os.getenv("USE_FAISS", "false").lower() == "true"

def retrieve_context(question: str, top_k: int = 5):
    if not FAISS_ENABLED:
        # Fallback: no vector search
        return []

    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        import json
        import numpy as np

        model = SentenceTransformer("all-MiniLM-L6-v2")
        index = faiss.read_index("rag/vector_store.faiss")

        with open("rag/metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        query_embedding = model.encode([question]).astype("float32")
        distances, indices = index.search(query_embedding, top_k)

        return [metadata[i] for i in indices[0] if i < len(metadata)]

    except Exception as e:
        print("FAISS disabled or failed:", e)
        return []
