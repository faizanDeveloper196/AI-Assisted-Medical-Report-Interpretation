import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import os
import logging

# Skip the slow "Checking connectivity to the model hosters" step
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

logger = logging.getLogger(__name__)

# ── Tesseract OCR (fast, ~1-2s) ────────────────────────────────────────────

def _tesseract_available():
    """Check if Tesseract is installed."""
    try:
        import pytesseract
        for path in [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False

_use_tesseract = _tesseract_available()

# ── PaddleOCR (fallback, heavy) ────────────────────────────────────────────

_paddle_ocr = None

def _get_paddle_ocr():
    global _paddle_ocr
    if _paddle_ocr is None:
        from paddleocr import PaddleOCR
        _paddle_ocr = PaddleOCR(
            lang='en',
            enable_mkldnn=False,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
    return _paddle_ocr

# ── Main OCR function ──────────────────────────────────────────────────────

def extract_text_from_image(image_path):
    """
    Extracts text from an image.
    Uses Tesseract (fast) if available, otherwise PaddleOCR (slow).
    """
    if _use_tesseract:
        return _extract_with_tesseract(image_path)
    return _extract_with_paddle(image_path)


def _extract_with_tesseract(image_path):
    """Fast OCR using Tesseract (~1-3 seconds) with image preprocessing."""
    try:
        import pytesseract
        from PIL import ImageFilter, ImageEnhance
        pil_image = Image.open(image_path).convert('RGB')

        # Upscale small images for better Tesseract accuracy
        w, h = pil_image.size
        if max(w, h) < 2000:
            scale = 2
            pil_image = pil_image.resize((w * scale, h * scale), Image.LANCZOS)

        # Convert to grayscale and enhance contrast
        gray = pil_image.convert('L')
        gray = ImageEnhance.Contrast(gray).enhance(1.5)
        gray = gray.filter(ImageFilter.SHARPEN)

        custom_config = r'--oem 3 --psm 6'
        return pytesseract.image_to_string(gray, config=custom_config)
    except Exception as e:
        logger.error(f"Tesseract OCR Error: {e}")
        return _extract_with_paddle(image_path)


def _extract_with_paddle(image_path):
    """Heavy OCR using PaddleOCR (fallback)."""
    try:
        ocr = _get_paddle_ocr()
        pil_image = Image.open(image_path).convert('RGB')

        # Resize large images to speed up OCR
        MAX_DIM = 1500
        w, h = pil_image.size
        if max(w, h) > MAX_DIM:
            scale = MAX_DIM / max(w, h)
            pil_image = pil_image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        img_array = np.array(pil_image)
        result = ocr.ocr(img_array)

        text_parts = []
        if not result:
            return ""

        for page in result:
            if page is None:
                continue
            if isinstance(page, dict):
                rec_texts = page.get('rec_texts', [])
                if rec_texts:
                    text_parts.extend([str(t) for t in rec_texts if t])
                    continue
                for key in ('ocr_result', 'text_line_boxes', 'result'):
                    sub = page.get(key)
                    if sub and isinstance(sub, list):
                        for item in sub:
                            if isinstance(item, dict) and 'text' in item:
                                text_parts.append(item['text'])
                        break
            elif isinstance(page, list):
                for item in page:
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        text_conf = item[1]
                        if isinstance(text_conf, (list, tuple)) and len(text_conf) >= 1:
                            text_parts.append(str(text_conf[0]))

        return " ".join(text_parts)

    except Exception as e:
        logger.error(f"PaddleOCR Error: {e}")
        raise


def pdf_to_images(pdf_path):
    """Converts a PDF to a list of temporary image paths."""
    images = convert_from_path(pdf_path)
    image_paths = []
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    temp_dir = os.path.dirname(pdf_path)
    for i, img in enumerate(images):
        path = os.path.join(temp_dir, f"{base_name}_page_{i}.png")
        img.save(path, 'PNG')
        image_paths.append(path)
    return image_paths
