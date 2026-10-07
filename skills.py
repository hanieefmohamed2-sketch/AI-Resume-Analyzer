"""
skills.py

Detects technical skills present in resume text using keyword matching
against a reference skills database. Provides a deterministic,
explainable cross-check against AI-reported skills (Lesson 9) and
feeds the ATS scorer (Lesson 10).
"""

import re
from typing import List


# A reference list of common technical skills to check for.
# In a real production system, this might live in a database or JSON
# file and be regularly updated — we keep it as a simple list for learning.
SKILLS_DATABASE: List[str] = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "r",
    "sql", "nosql", "mongodb", "postgresql", "mysql",
    "django", "flask", "fastapi", "react", "angular", "vue",
    "streamlit", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux",
    "rest api", "graphql", "machine learning", "deep learning",
    "data analysis", "data visualization", "nlp",
]


def detect_skills(resume_text: str) -> List[str]:
    """
    Detects which known technical skills appear in the given resume text,
    using whole-word matching to avoid false positives from substrings.

    Args:
        resume_text: The cleaned resume text to scan.

    Returns:
        A list of detected skills (using their canonical, title-cased
        form), in the order they appear in SKILLS_DATABASE.
    """
    text_lower = resume_text.lower()
    found_skills = []

    for skill in SKILLS_DATABASE:
        # Build a word-boundary pattern for this specific skill.
        # re.escape() ensures special characters (like '+' in "c++")
        # are treated literally, not as regex syntax.
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text_lower):
            found_skills.append(skill.title())

    return found_skills


def find_missing_skills(found_skills: List[str], target_role_skills: List[str]) -> List[str]:
    """
    Compares detected skills against a target list (e.g., skills typically
    expected for a specific job role) and returns which ones are missing.

    Args:
        found_skills: Skills already detected in the resume.
        target_role_skills: Skills expected for a target role/job.

    Returns:
        A list of skills present in target_role_skills but not in found_skills.
    """
    found_lower = {s.lower() for s in found_skills}
    missing = [s for s in target_role_skills if s.lower() not in found_lower]
    return missing