import requests
import json
import re

def extract_values_with_llm(raw_text):
    """
    Uses the local LLM (Ollama) to dynamically extract ALL medical test values
    from the raw OCR text. Returns a dict of {test_name: value}.
    Much more flexible than hardcoded regex patterns.
    """
    if not raw_text or not raw_text.strip():
        return {}

    prompt = f"""You are a medical report parser. Extract ALL lab test names and their numeric values from this text.

Return ONLY a valid JSON object like this:
{{"hemoglobin": 13.5, "glucose": 95, "wbc": 7.2}}

Rules:
- Use lowercase snake_case keys (e.g., "wbc", "rbc", "hemoglobin")
- Values must be numbers only (no units)
- Skip any non-numeric or unclear values
- Return ONLY the JSON, no explanation

Text to parse:
{raw_text}

JSON:"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:8b",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        llm_response = response.json().get("response", "").strip()
        print(f"[LLM PARSER] Response: {llm_response[:300]}")

        # Extract the JSON from the response (in case LLM adds extra text)
        json_match = re.search(r'\{[^{}]+\}', llm_response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            # Ensure all values are floats
            return {k: float(v) for k, v in parsed.items() if isinstance(v, (int, float))}
        return {}

    except Exception as e:
        print(f"[LLM PARSER] Error: {e}")
        # Fallback to regex if LLM fails
        return extract_values_regex(raw_text)


def extract_values_regex(text):
    """
    Fallback regex-based extractor for common medical tests.
    """
    values = {}
    patterns = {
        "hemoglobin": r'Hemoglobin[\s\S]*?(\d+\.?\d*)',
        "glucose":    r'Glucose[\s\S]*?(\d+\.?\d*)',
        "rbc":        r'RBC[\s\S]*?(\d+\.?\d*)',
        "wbc":        r'WBC[\s\S]*?(\d+\.?\d*)',
        "platelets":  r'Platelet[\s\S]*?(\d+\.?\d*)',
        "creatinine": r'Creatinine[\s\S]*?(\d+\.?\d*)',
        "ast":        r'\bAST[\s\S]*?(\d+\.?\d*)',
        "alt":        r'\bALT[\s\S]*?(\d+\.?\d*)',
        "cholesterol":r'Cholesterol[\s\S]*?(\d+\.?\d*)',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                values[key] = float(match.group(1))
            except ValueError:
                continue
    return values


def extract_values(text):
    """
    Main entry point: tries LLM extraction first, falls back to regex.
    """
    return extract_values_with_llm(text)
