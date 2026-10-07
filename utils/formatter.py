"""
utils/formatter.py

Contains text formatting and cleaning utilities.
Used to prepare raw extracted resume text before analysis.
"""

import re


def clean_text(raw_text: str) -> str:
    """
    Cleans raw text extracted from a PDF by removing extra whitespace,
    decorative bullet characters, and excessive blank lines.

    Args:
        raw_text: The unprocessed text, typically from pdf_reader.py.

    Returns:
        A cleaned, normalized string ready for analysis.
    """
    if not raw_text:
        return ""

    text = raw_text

   # Normalize line endings (CRLF/CR -> LF)
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Remove common decorative bullet characters (•, ●, ▪, ‣, ◦, -, *, etc.)
    # used at the start of lines in resumes
    text = re.sub(r'(?m)^[ \t]*[•●▪‣◦∙·–—*]+[ \t]*', '', text)

    # Collapse multiple spaces/tabs into a single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Strip trailing whitespace on each line
    text = re.sub(r'(?m)[ \t]+$', '', text)

    # Collapse 3+ consecutive newlines into just 2 (max one blank line)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove leading/trailing whitespace from the whole text
    text = text.strip()

    return text