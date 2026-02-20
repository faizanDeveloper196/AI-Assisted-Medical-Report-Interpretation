import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import os
import logging

logger = logging.getLogger(__name__)

# Initialize OCR engine lazily
_ocr = None

def get_ocr():
    global _ocr
    if _ocr is None:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(use_angle_cls=True, lang='en', enable_mkldnn=False)
    return _ocr

def extract_text_from_image(image_path):
    """
    Extracts text from an image using PaddleOCR.
    Converts image to numpy array first to avoid path/glob issues.
    """
    try:
        ocr = get_ocr()

        # Open with PIL and convert to numpy array (avoids path issues in PaddleOCR 3.x)
        pil_image = Image.open(image_path).convert('RGB')
        img_array = np.array(pil_image)

        result = ocr.ocr(img_array)
        print(f"[OCR] Raw result type: {type(result)}")
        print(f"[OCR] Raw result: {str(result)[:500]}")

        text_parts = []

        if not result:
            return ""

        for page in result:
            if page is None:
                continue

            # --- PaddleOCR 3.x format (PaddleX-based) ---
            # Result is a dict with 'rec_texts' key
            if isinstance(page, dict):
                rec_texts = page.get('rec_texts', [])
                if rec_texts:
                    text_parts.extend([str(t) for t in rec_texts if t])
                    continue

                # Sometimes nested inside 'ocr_result' or similar
                for key in ('ocr_result', 'text_line_boxes', 'result'):
                    sub = page.get(key)
                    if sub and isinstance(sub, list):
                        for item in sub:
                            if isinstance(item, dict) and 'text' in item:
                                text_parts.append(item['text'])
                        break

            # --- Old PaddleOCR 2.x format ---
            # Result is a list of [bbox, (text, confidence)]
            elif isinstance(page, list):
                for item in page:
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        text_conf = item[1]
                        if isinstance(text_conf, (list, tuple)) and len(text_conf) >= 1:
                            text_parts.append(str(text_conf[0]))

        extracted = " ".join(text_parts)
        print(f"[OCR] Extracted text ({len(extracted)} chars): {extracted[:300]}")
        return extracted

    except Exception as e:
        logger.error(f"OCR Error: {e}")
        raise

def pdf_to_images(pdf_path):
    """
    Converts a PDF to a list of temporary image paths.
    """
    images = convert_from_path(pdf_path)
    image_paths = []
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    temp_dir = os.path.dirname(pdf_path)
    for i, img in enumerate(images):
        path = os.path.join(temp_dir, f"{base_name}_page_{i}.png")
        img.save(path, 'PNG')
        image_paths.append(path)
    return image_paths
