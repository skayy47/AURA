from __future__ import annotations

from pdf2image import convert_from_bytes
import pytesseract


def load_pdf_to_text(uploaded_file, poppler_path: str) -> str:
    """
    Convert an uploaded PDF (Streamlit UploadedFile) to text using OCR.

    Steps:
    - Read file bytes from the uploaded file
    - Convert PDF pages to images using pdf2image + Poppler
    - Run Tesseract OCR on each image
    """
    pdf_bytes = uploaded_file.read()

    images = convert_from_bytes(pdf_bytes, poppler_path=poppler_path)

    texts = [pytesseract.image_to_string(img) for img in images]

    return "\n\n".join(texts)
