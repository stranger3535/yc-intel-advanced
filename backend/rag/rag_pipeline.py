# backend/rag/rag_pipeline.py
from rag.retriever import retrieve_context
from services.gemini_client import generate_answer

def answer_question(question: str) -> dict:
    context = retrieve_context(question)

    prompt = f"""
You are an analyst for Y Combinator data.

Context:
{context}

Question:
{question}
"""

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "sources": context,
    }
