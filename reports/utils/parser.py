import requests
import json
import re
import logging

logger = logging.getLogger(__name__)


def extract_values_with_llm(raw_text):
    """
    Uses the local LLM (Ollama) to dynamically extract ALL medical test values
    from the raw OCR text. Returns a dict of {test_name: value}.
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

        json_match = re.search(r'\{[^{}]+\}', llm_response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return {k: float(v) for k, v in parsed.items() if isinstance(v, (int, float))}
        return {}

    except Exception as e:
        logger.error(f"LLM Parser Error: {e}")
        return extract_values_regex(raw_text)


def extract_values_regex(text):
    """
    Regex-based extractor for medical tests.
    Patterns are OCR-tolerant to handle common misreads (e.g., Hemagabin for Hemoglobin).
    """
    values = {}
    patterns = {
        "hemoglobin": r'(?:H[ae]m[ao]g[lo][ob]bin|Hgb|HGB|Hb\b)[\s\S]*?(\d+\.?\d*)',
        "glucose":    r'Gl[uo]c[oa]se[\s\S]*?(\d+\.?\d*)',
        "rbc":        r'(?:RBC|R\.?B\.?C|Red\s*Blood)[\s\S]*?(\d+\.?\d*)',
        "wbc":        r'(?:WBC|W\.?B\.?C|White\s*Blood|Total\s*(?:WBC|Leucocyte))[\s\S]*?(\d+\.?\d*)',
        "platelets":  r'(?:Pl[ai][at]elet|PLT)[\s\S]*?(\d+\.?\d*)',
        "creatinine": r'Cr[ea][ea]t[il]nine[\s\S]*?(\d+\.?\d*)',
        "ast":        r'\bAST[\s\S]*?(\d+\.?\d*)',
        "alt":        r'\bALT[\s\S]*?(\d+\.?\d*)',
        "cholesterol":r'Chol[ea]st[ea]r[oa]l[\s\S]*?(\d+\.?\d*)',
        "pcv":        r'(?:PCV|Packed\s*Cell|Hematocrit|HCT)[\s\S]*?(\d+\.?\d*)',
        "mcv":        r'\bMCV[\s\S]*?(\d+\.?\d*)',
        "mch":        r'\bMCH\b[\s\S]*?(\d+\.?\d*)',
        "mchc":       r'\bMCHC[\s\S]*?(\d+\.?\d*)',
        "neutrophils":r'Neutr[oa]ph[il]l[\s\S]*?(\d+\.?\d*)',
        "lymphocytes":r'Lymph[oa]cyte[\s\S]*?(\d+\.?\d*)',
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
    Main entry point: tries fast regex first, falls back to LLM if no results.
    """
    regex_result = extract_values_regex(text)
    if regex_result:
        return regex_result
    return extract_values_with_llm(text)
