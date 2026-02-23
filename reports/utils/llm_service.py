import requests
import json
import re
import logging

logger = logging.getLogger(__name__)


def generate_summary(test, value, status, mode="short"):
    """
    Generates a simple explanation using a local LLM (Ollama).
    Kept as fallback for single-test queries.
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
                "model": "llama3:8b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "Analysis unavailable.")
    except requests.exceptions.ConnectionError:
        return "⚠️ AI summary unavailable — please ensure Ollama is running (`ollama serve`)."
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return "AI Analysis unavailable."


def generate_summaries_batch(test_results):
    """
    Generates explanations for ALL tests in a SINGLE LLM call.
    test_results: list of (test_name, value, status) tuples
    Returns: dict of {test_name: summary_string}
    """
    if not test_results:
        return {}

    tests_block = "\n".join(
        f"- {name}: {value} ({status})"
        for name, value, status in test_results
    )

    prompt = f"""You are a medical assistant. Explain each lab result below in simple language for a patient.
Keep each explanation to 1-2 sentences. Do NOT diagnose.

Lab Results:
{tests_block}

Return ONLY a valid JSON object mapping each test name to its explanation, like:
{{"hemoglobin": "Your hemoglobin is normal...", "glucose": "Your glucose level..."}}

JSON:"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:8b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 300,
                    "temperature": 0.3,
                }
            },
            timeout=180
        )
        response.raise_for_status()
        llm_response = response.json().get("response", "").strip()

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', llm_response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            summaries = {k: str(v) for k, v in parsed.items()}
            for name, value, status in test_results:
                if name not in summaries:
                    summaries[name] = f"Your {name.replace('_', ' ')} is {value} ({status})."
            return summaries

    except requests.exceptions.ConnectionError:
        pass
    except Exception as e:
        logger.error(f"LLM Batch Error: {e}")

    # Fallback: generate simple non-LLM summaries
    return {
        name: f"Your {name.replace('_', ' ')} level is {value}, which is {status.lower()}."
        for name, value, status in test_results
    }
