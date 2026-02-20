from .ocr_service import extract_text_from_image, pdf_to_images
from .parser import extract_values
from .range_engine import check_ranges
from .llm_service import generate_summary
import os

def process_report(file_path):
    """
    Orchestrates the medical report processing flow.
    """
    
    # 1. OCR Layer
    text = ""
    if file_path.lower().endswith('.pdf'):
        image_paths = pdf_to_images(file_path)
        for img_path in image_paths:
            text += extract_text_from_image(img_path) + " "
            # Cleanup temp images
            try:
                os.remove(img_path)
            except:
                pass
    else:
        text = extract_text_from_image(file_path)

    # 2. Structured Medical Value Extraction
    values = extract_values(text)

    # 3. Reference Range Knowledge Layer
    statuses = check_ranges(values) # Returns "Low", "Normal", "High"

    # 4. LLM-Based Explanation
    summaries = {}
    for test, value in values.items():
        # Get status from the statuses dict, using specific status for LLM context
        status = statuses[test]
        summaries[test] = generate_summary(test, value, status, mode="short")

    return {
        "raw_text": text,
        "values": values,
        "statuses": statuses,
        "summaries": summaries
    }
