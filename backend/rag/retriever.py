# backend/rag/retriever.py
import os

FAISS_ENABLED = os.getenv("USE_FAISS", "false").lower() == "true"

def retrieve_context(question: str, top_k: int = 5):
    if not FAISS_ENABLED:
        raise RuntimeError("FAISS is disabled. RAG cannot run without context.")

    try:
        import faiss
        import json
        import numpy as np
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        index = faiss.read_index("rag/vector_store.faiss")

        with open("rag/metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Encode question
        query_embedding = model.encode([question]).astype("float32")

        #  THIS MUST COME FIRST
        distances, indices = index.search(query_embedding, top_k)

        results = []

        #  NOW distances IS DEFINED
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(metadata) and dist < 1.2:  # relevance threshold
                results.append(metadata[idx])

        return results

    except Exception as e:
        print("FAISS disabled or failed:", e)
        return []