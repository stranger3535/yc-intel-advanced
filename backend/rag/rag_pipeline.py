import subprocess
from rag.retriever import retrieve_context

OLLAMA_PATH = r"C:\Users\abhij\AppData\Local\Programs\Ollama\ollama.exe"

def answer_question(question: str) -> str:
    # 1. Retrieve context
    contexts = retrieve_context(question)

    if not contexts:
        context_text = "No relevant company data found."
    else:
        context_text = "\n\n".join(
            f"- {c['name']} ({c.get('domain','')}): {c.get('description','')}"
            for c in contexts
        )

    # 2. Build prompt
    prompt = f"""
You are an analyst answering questions about Y Combinator companies.

Context:
{context_text}

Question:
{question}

Answer clearly and concisely.
"""

    # 3. Call Ollama
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", "llama3"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )
    except Exception as e:
        return f"Ollama execution failed: {e}"

    if result.returncode != 0:
        return f"Ollama error: {result.stderr}"

    return result.stdout.strip()
