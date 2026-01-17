import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ------------------ CONFIG ------------------
INDEX_PATH = "backend/rag/vector_store.faiss"
META_PATH = "backend/rag/metadata.json"
TOP_K = 5

# Load model + index once
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(INDEX_PATH)

with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)


def retrieve_context(question: str, top_k: int = TOP_K) -> list[str]:
    query_embedding = model.encode([question]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        if idx < len(metadata):
            results.append(metadata[idx])

    return results
