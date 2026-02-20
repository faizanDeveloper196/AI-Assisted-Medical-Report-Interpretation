import requests
import json

def generate_summary(test, value, status, mode="short"):
    """
    Generates a simple explanation using a local LLM (Ollama).
    """
    prompt = f"""
    Explain this lab result in simple language for a patient.
    Test: {test}
    Value: {value}
    Status: {status}
    Keep it very short (1-2 sentences). Do NOT diagnose.
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:8b", # User specified model
                "prompt": prompt,
                "stream": False
            },
            timeout=30 # Add timeout to prevent hanging
        )
        response.raise_for_status()
        return response.json().get("response", "Analysis unavailable.")
    except requests.exceptions.ConnectionError:
        return "⚠️ AI summary unavailable — please ensure Ollama is running (`ollama serve`)."
    except Exception as e:
        print(f"LLM Error: {e}")
        return "AI Analysis unavailable."
