from .ocr_service import extract_text_from_image, pdf_to_images
from .parser import extract_values
from .range_engine import check_ranges
from .llm_service import generate_summaries_batch
from concurrent.futures import ThreadPoolExecutor
import os


def process_report(file_path):
    """
    Orchestrates the medical report processing flow.
    Optimized: uses batch LLM call and concurrent OCR.
    """

    # 1. OCR Layer
    text = ""
    if file_path.lower().endswith('.pdf'):
        image_paths = pdf_to_images(file_path)
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(extract_text_from_image, image_paths))
        text = " ".join(results)
        for img_path in image_paths:
            try:
                os.remove(img_path)
            except Exception:
                pass
    else:
        text = extract_text_from_image(file_path)

    # 2. Structured Medical Value Extraction
    values = extract_values(text)

    # 3. Reference Range Knowledge Layer
    statuses = check_ranges(values)

    # 4. LLM-Based Explanation — single batch call
    test_results = [(test, value, statuses[test]) for test, value in values.items()]
    summaries = generate_summaries_batch(test_results)

    return {
        "raw_text": text,
        "values": values,
        "statuses": statuses,
        "summaries": summaries
    }
