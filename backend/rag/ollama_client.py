import subprocess

def ask_llama(prompt: str) -> str:
    process = subprocess.Popen(
        ["ollama", "run", "llama3"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",     # ✅ FIX
        errors="ignore"       # ✅ FIX
    )

    stdout, stderr = process.communicate(prompt)

    if stderr:
        return "LLM error occurred"

    return stdout.strip()
