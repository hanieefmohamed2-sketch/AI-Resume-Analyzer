"""
ats.py

Rule-based ATS (Applicant Tracking System) scoring logic.
Complements the AI-generated score with a transparent, explainable,
deterministic scoring system based on common real-world ATS checks.
"""

import re
from typing import List, Dict, Any


# Standard resume section headers that ATS systems typically look for
STANDARD_SECTIONS = [
    "experience", "education", "skills", "summary",
    "projects", "certifications", "objective"
]


def _check_section_headers(text: str) -> tuple[int, str]:
    """Checks for the presence of standard resume section headers."""
    text_lower = text.lower()
    found = [s for s in STANDARD_SECTIONS if s in text_lower]

    # Award points proportional to how many standard sections were found
    points = min(20, len(found) * 5)
    reason = f"Found {len(found)} standard section(s): {', '.join(found) or 'none'}"

    return points, reason


def _check_contact_info(text: str) -> tuple[int, str]:
    """Checks for the presence of an email address and a phone number."""
    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
    has_phone = bool(re.search(r"(\+?\d[\d\s\-()]{8,}\d)", text))

    points = 0
    if has_email:
        points += 8
    if has_phone:
        points += 7

    reason = f"Email found: {has_email}, Phone found: {has_phone}"
    return points, reason


def _check_length(text: str) -> tuple[int, str]:
    """Checks whether the resume length is within a reasonable range."""
    word_count = len(text.split())

    if 300 <= word_count <= 1200:
        points = 15
    elif 150 <= word_count < 300 or 1200 < word_count <= 1600:
        points = 8
    else:
        points = 3

    reason = f"Resume has {word_count} words"
    return points, reason


def _check_skills_count(skills_found: List[str]) -> tuple[int, str]:
    """Awards points based on the number of distinct skills detected."""
    count = len(skills_found)
    points = min(30, count * 3)
    reason = f"{count} skill(s) detected"
    return points, reason


def _check_quantified_achievements(text: str) -> tuple[int, str]:
    """Checks for numbers/percentages, a sign of quantified achievements."""
    matches = re.findall(r"\b\d+%|\b\d+\+|\$\d+", text)
    points = min(20, len(matches) * 4)
    reason = f"Found {len(matches)} quantified achievement(s)"
    return points, reason


def calculate_ats_score(resume_text: str, skills_found: List[str]) -> Dict[str, Any]:
    """
    Calculates a rule-based ATS compatibility score out of 100, broken
    down by individual check categories for transparency.

    Args:
        resume_text: The cleaned resume text.
        skills_found: A list of skills (typically from the AI analysis).

    Returns:
        A dictionary with the total score and a breakdown of each check,
        e.g. {"total_score": 76, "breakdown": {...}}
    """
    checks = {
        "section_headers": _check_section_headers(resume_text),
        "contact_info": _check_contact_info(resume_text),
        "length": _check_length(resume_text),
        "skills_count": _check_skills_count(skills_found),
        "quantified_achievements": _check_quantified_achievements(resume_text),
    }

    total_score = sum(points for points, _ in checks.values())
    total_score = min(100, total_score)

    breakdown = {name: {"points": points, "reason": reason}
                 for name, (points, reason) in checks.items()}

    return {
        "total_score": total_score,
        "breakdown": breakdown,
    }