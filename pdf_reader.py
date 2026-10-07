"""
pdf_reader.py

Responsible for extracting raw text from an uploaded PDF resume.
This module has ONE job: PDF -> plain text. Nothing else.
"""

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from typing import Optional


def extract_text_from_pdf(uploaded_file) -> Optional[str]:
    """
    Extracts all readable text from a PDF file.
    Supports pdfplumber and pypdf with automatic fallback.
    """
    extracted_text = ""

    try:
        if pdfplumber is not None:
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"
                if extracted_text.strip():
                    return extracted_text
            except Exception as e:
                print(f"pdfplumber failed, trying pypdf fallback: {e}")

        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

        if PdfReader is not None:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"

    except Exception as e:
        print(f"Error while reading PDF: {e}")
        return None

    if not extracted_text.strip():
        return None

    return extracted_text