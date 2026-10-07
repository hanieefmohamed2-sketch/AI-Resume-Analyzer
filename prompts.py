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

IMPROVEMENT_SUGGESTIONS_PROMPT_TEMPLATE = """
You are an expert career coach. Below is a candidate's resume, along with
concrete computed facts about it. Use these SPECIFIC facts to generate
SPECIFIC, non-generic improvement suggestions — avoid vague advice that
could apply to any resume.

Resume text:
---
{resume_text}
---

Computed ATS score: {ats_score}/100
ATS score breakdown:
{ats_breakdown}

Skills detected: {skills_found}
Skills that may be missing for a typical role in this field: {missing_skills}

Based on these SPECIFIC facts (not generic resume advice), provide exactly
5 improvement suggestions. Each suggestion must reference something
concrete from the facts above (e.g., a specific missing skill, a specific
low-scoring ATS category, or a specific weak section).

Respond ONLY with a valid JSON object in this exact structure:

{{
  "improvement_suggestions": [
    "<specific suggestion 1>",
    "<specific suggestion 2>",
    "<specific suggestion 3>",
    "<specific suggestion 4>",
    "<specific suggestion 5>"
  ]
}}
"""


def build_improvement_prompt(
    resume_text: str,
    ats_score: int,
    ats_breakdown: dict,
    skills_found: list,
    missing_skills: list,
) -> str:
    """
    Builds a context-enriched prompt for generating specific, grounded
    improvement suggestions, using computed ATS and skills data.

    Args:
        resume_text: The cleaned resume text.
        ats_score: The rule-based ATS score from ats.py.
        ats_breakdown: The score breakdown dict from ats.py.
        skills_found: Skills detected by skills.py.
        missing_skills: Skills identified as missing.

    Returns:
        A complete prompt string ready to send to the AI model.
    """
    # Format the breakdown dict into readable lines for the prompt
    breakdown_lines = "\n".join(
        f"- {category}: {details['points']} points ({details['reason']})"
        for category, details in ats_breakdown.items()
    )

    return IMPROVEMENT_SUGGESTIONS_PROMPT_TEMPLATE.format(
        resume_text=resume_text,
        ats_score=ats_score,
        ats_breakdown=breakdown_lines,
        skills_found=", ".join(skills_found) if skills_found else "None detected",
        missing_skills=", ".join(missing_skills) if missing_skills else "None identified",
    )

INTERVIEW_QUESTIONS_PROMPT_TEMPLATE = """
You are a senior technical interviewer preparing to interview this specific
candidate. You have read their resume carefully and now need to prepare
questions that reference SPECIFIC details from it — not generic interview
questions that could apply to anyone.

Resume text:
---
{resume_text}
---

Skills this candidate claims: {skills_found}
Skills commonly expected for this field that seem absent: {missing_skills}

Generate exactly 7 interview questions following these rules:
- At least 3 questions must directly reference a specific project,
  achievement, number, or company mentioned in the resume text above.
- At least 2 questions must be technical, testing depth of knowledge in
  a specific skill the candidate claims to have.
- At least 1 question must probe a gap — for example, asking how the
  candidate handled something related to a missing skill, or asking for
  evidence behind a claimed skill that has no supporting project/detail.
- At least 1 question should be behavioral, grounded in a specific
  experience mentioned in the resume (not a generic behavioral question).

Respond ONLY with a valid JSON object in this exact structure:

{{
  "interview_questions": [
    {{"question": "<question text>", "type": "<technical|behavioral|gap-probing>", "based_on": "<short note on what resume detail this references>"}},
    ...
  ]
}}
"""


def build_interview_questions_prompt(
    resume_text: str,
    skills_found: list,
    missing_skills: list,
) -> str:
    """
    Builds a prompt for generating interview questions grounded in
    specific resume content, rather than generic question banks.

    Args:
        resume_text: The cleaned resume text.
        skills_found: Skills detected in the resume.
        missing_skills: Skills identified as potentially missing.

    Returns:
        A complete prompt string ready to send to the AI model.
    """
    return INTERVIEW_QUESTIONS_PROMPT_TEMPLATE.format(
        resume_text=resume_text,
        skills_found=", ".join(skills_found) if skills_found else "None detected",
        missing_skills=", ".join(missing_skills) if missing_skills else "None identified",
    )