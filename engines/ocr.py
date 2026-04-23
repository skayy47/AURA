"""PDF OCR engine — converts uploaded PDFs to plain text via Tesseract."""
from __future__ import annotations

from pdf2image import convert_from_bytes
import pytesseract

from utils.helpers import get_logger

logger = get_logger(__name__)


def load_pdf_to_text(uploaded_file, poppler_path: str) -> str:
    """
    Convert an uploaded PDF (Streamlit UploadedFile) to text using OCR.

    Steps:
    - Read file bytes from the uploaded file
    - Convert PDF pages to images using pdf2image + Poppler
    - Run Tesseract OCR on each image
    """
    pdf_bytes = uploaded_file.read()
    logger.info("OCR: converting PDF (%d bytes) with Poppler at %s", len(pdf_bytes), poppler_path)

    images = convert_from_bytes(pdf_bytes, poppler_path=poppler_path)
    logger.info("OCR: extracted %d page(s)", len(images))

    texts = [pytesseract.image_to_string(img) for img in images]
    return "\n\n".join(texts)
