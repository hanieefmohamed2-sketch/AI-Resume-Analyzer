"""
pdf_reader.py

Responsible for extracting raw text from an uploaded PDF resume.
This module has ONE job: PDF -> plain text. Nothing else.
"""

import pdfplumber
from typing import Optional


def extract_text_from_pdf(uploaded_file) -> Optional[str]:
    """
    Extracts all readable text from a PDF file.

    Args:
        uploaded_file: A file-like object (e.g., from Streamlit's file_uploader,
                        or a standard Python file opened in 'rb' mode).

    Returns:
        A single string containing all extracted text from every page,
        or None if no text could be extracted.
    """
    extracted_text = ""

    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"

    except Exception as e:
        print(f"Error while reading PDF: {e}")
        return None

    if not extracted_text.strip():
        return None

    return extracted_text