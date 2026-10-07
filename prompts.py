"""
prompts.py

Stores prompt templates used to instruct the AI model.
Keeping prompts separate from API-calling logic means we can
refine prompt wording without touching analyzer.py.
"""


RESUME_ANALYSIS_PROMPT_TEMPLATE = """
You are an expert ATS (Applicant Tracking System) analyzer and professional
career coach with 15 years of experience in technical recruiting.

Here is the candidate's resume text:
---
{resume_text}
---

Analyze this resume and provide a complete assessment including:
- An ATS compatibility score out of 100
- A 2-3 sentence professional summary
- A list of technical skills found in the resume
- A list of important, commonly-expected skills that seem to be missing
- Exactly 3 key strengths
- Exactly 3 key weaknesses
- Exactly 3 specific, actionable improvement suggestions
- Exactly 3 recommended certifications
- Exactly 3 suggested projects to build to strengthen this resume
- Exactly 3 technologies worth learning next
- Exactly 3 recommended job roles this resume is best suited for
- Exactly 5 likely interview questions based on this specific resume's content

Respond ONLY with a valid JSON object. Do not include any text, explanation,
or markdown code fences before or after the JSON. Use exactly this structure:

{{
  "ats_score": <integer 0-100>,
  "summary": "<string>",
  "skills_found": ["...", "..."],
  "missing_skills": ["...", "..."],
  "strengths": ["...", "...", "..."],
  "weaknesses": ["...", "...", "..."],
  "improvement_suggestions": ["...", "...", "..."],
  "recommended_certifications": ["...", "...", "..."],
  "suggested_projects": ["...", "...", "..."],
  "technologies_to_learn": ["...", "...", "..."],
  "recommended_roles": ["...", "...", "..."],
  "interview_questions": ["...", "...", "...", "...", "..."]
}}
"""


def build_analysis_prompt(resume_text: str) -> str:
    """
    Fills the resume analysis prompt template with the given resume text.

    Args:
        resume_text: The cleaned resume text to analyze.

    Returns:
        A complete prompt string ready to send to the AI model.
    """
    return RESUME_ANALYSIS_PROMPT_TEMPLATE.format(resume_text=resume_text)