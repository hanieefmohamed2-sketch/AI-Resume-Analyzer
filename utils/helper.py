"""
utils/helper.py

General-purpose helper functions used across the project.
"""

from pathlib import Path


def load_css(file_path: str) -> str:
    """
    Reads a CSS file from disk and returns its contents wrapped in
    a <style> tag, ready to pass into st.markdown().

    Args:
        file_path: Path to the .css file, relative to the project root.

    Returns:
        A string containing the CSS wrapped in <style></style> tags.
    """
    css_path = Path(file_path)

    if not css_path.exists():
        return ""

    css_content = css_path.read_text(encoding="utf-8")
    return f"<style>{css_content}</style>"