from rag.retriever import retrieve_context
from rag.ollama_client import generate_answer
from prompts.system_prompt import YC_SYSTEM_PROMPT


def answer_question(question: str) -> dict:
    context = retrieve_context(question)

    if not context:
        return {
            "answer": "I don’t have information about that in the YC dataset.",
            "sources": []
        }

    prompt = f"""
You are an analyst for Y Combinator data.
Use ONLY the context below.
If the answer is not in the context, say you don’t know.

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