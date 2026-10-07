"""
app.py
 
Streamlit front-end for the AI Resume Analyzer.
 
Wires together the existing modules:
    pdf_reader.py  -> PDF text extraction
    formatter.py   -> text cleaning
    analyzer.py    -> AI call + JSON parsing
    config.py      -> shared settings / constraints
 
This file owns ONLY presentation & flow control. It intentionally
contains no PDF-parsing, prompt-building, or API-calling logic —
that all stays in the modules above.
"""
 
import streamlit as st
 
import config
from pdf_reader import extract_text_from_pdf
from formatter import clean_text
from analyzer import analyze_resume
 
 
# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------
 
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# Minimal styling polish (kept in-file since this is a single-page app)
st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; }
        .stMetric { background: rgba(127,127,127,0.08); padding: 1rem;
                    border-radius: 0.75rem; }
        .streak-tag { display:inline-block; padding: 0.15rem 0.6rem;
                      margin: 0.15rem; border-radius: 999px;
                      background: rgba(127,127,127,0.12); font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
 
 
# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
 
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = None
 
 
# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
 
with st.sidebar:
    st.header("📄 AI Resume Analyzer")
    st.caption("Upload a PDF resume and get an AI-powered ATS assessment.")
 
    st.divider()
    st.subheader("Settings")
    st.write(f"**AI Provider:** `{config.AI_PROVIDER}`")
    st.write(f"**Max file size:** {config.MAX_FILE_SIZE_MB} MB")
    st.write(f"**Allowed types:** {', '.join(config.ALLOWED_FILE_TYPES).upper()}")
 
    if config.AI_PROVIDER == "openai" and not config.OPENAI_API_KEY:
        st.error("OPENAI_API_KEY is not set. Add it to your .env file.")
    if config.AI_PROVIDER == "gemini" and not config.GEMINI_API_KEY:
        st.error("GEMINI_API_KEY is not set. Add it to your .env file.")
 
    st.divider()
    if st.session_state.analysis_result is not None:
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.resume_filename = None
            st.rerun()
 
 
# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
 
def render_tag_list(items):
    """Render a list of strings as inline pill/tag chips."""
    if not items:
        st.caption("None found.")
        return
    tags_html = " ".join(f'<span class="streak-tag">{item}</span>' for item in items)
    st.markdown(tags_html, unsafe_allow_html=True)
 
 
def score_color(score: int) -> str:
    if score >= 80:
        return "🟢"
    if score >= 60:
        return "🟡"
    return "🔴"
 
 
def build_text_report(result: dict, filename: str) -> str:
    """Builds a plain-text version of the analysis for download."""
    lines = [
        "AI RESUME ANALYZER — REPORT",
        f"File: {filename}",
        "=" * 50,
        "",
        f"ATS Score: {result.get('ats_score', 'N/A')}/100",
        "",
        "SUMMARY",
        "-" * 50,
        result.get("summary", ""),
        "",
    ]
 
    sections = [
        ("SKILLS FOUND", "skills_found"),
        ("MISSING SKILLS", "missing_skills"),
        ("STRENGTHS", "strengths"),
        ("WEAKNESSES", "weaknesses"),
        ("IMPROVEMENT SUGGESTIONS", "improvement_suggestions"),
        ("RECOMMENDED CERTIFICATIONS", "recommended_certifications"),
        ("SUGGESTED PROJECTS", "suggested_projects"),
        ("TECHNOLOGIES TO LEARN", "technologies_to_learn"),
        ("RECOMMENDED ROLES", "recommended_roles"),
        ("LIKELY INTERVIEW QUESTIONS", "interview_questions"),
    ]
 
    for title, key in sections:
        lines.append(title)
        lines.append("-" * 50)
        for item in result.get(key, []) or []:
            lines.append(f"- {item}")
        lines.append("")
 
    return "\n".join(lines)
 
 
# --------------------------------------------------------------------------
# Main flow
# --------------------------------------------------------------------------
 
st.title("📄 AI Resume Analyzer")
st.write(
    "Upload your resume as a PDF and get an instant ATS compatibility "
    "score, skill gap analysis, and personalized career recommendations."
)
 
if st.session_state.analysis_result is None:
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF only)",
        type=config.ALLOWED_FILE_TYPES,
        accept_multiple_files=False,
    )
 
    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
 
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            st.error(
                f"File is {file_size_mb:.1f} MB, which exceeds the "
                f"{config.MAX_FILE_SIZE_MB} MB limit. Please upload a smaller file."
            )
        else:
            analyze_clicked = st.button("🔍 Analyze Resume", type="primary")
 
            if analyze_clicked:
                with st.spinner("Extracting text from PDF..."):
                    raw_text = extract_text_from_pdf(uploaded_file)
 
                if not raw_text:
                    st.error(
                        "Couldn't extract any text from this PDF. It may be a "
                        "scanned image or a corrupted file — try a text-based PDF."
                    )
                else:
                    cleaned_text = clean_text(raw_text)
 
                    if len(cleaned_text) < 50:
                        st.warning(
                            "The extracted text looks very short. Results may "
                            "not be reliable for such a brief document."
                        )
 
                    try:
                        with st.spinner("Analyzing resume with AI... this can take a few seconds."):
                            result = analyze_resume(cleaned_text)
 
                        st.session_state.analysis_result = result
                        st.session_state.resume_filename = uploaded_file.name
                        st.rerun()
 
                    except ValueError as e:
                        st.error(f"Analysis failed: {e}")
                    except Exception as e:
                        st.error(f"Unexpected error while analyzing resume: {e}")
 
else:
    # ----------------------------------------------------------------
    # Results view
    # ----------------------------------------------------------------
    result = st.session_state.analysis_result
    filename = st.session_state.resume_filename
 
    st.success(f"Analysis complete for **{filename}**")
 
    score = result.get("ats_score", 0)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("ATS Score", f"{score}/100", label_visibility="visible")
        st.write(f"{score_color(score)} Overall compatibility")
    with col2:
        st.subheader("Summary")
        st.write(result.get("summary", "No summary available."))
 
    st.divider()
 
    tab_skills, tab_swot, tab_growth, tab_prep = st.tabs(
        ["🧩 Skills", "⚖️ Strengths & Weaknesses", "🚀 Growth Plan", "🎤 Interview Prep"]
    )
 
    with tab_skills:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("✅ Skills Found")
            render_tag_list(result.get("skills_found", []))
        with col_b:
            st.subheader("❗ Missing Skills")
            render_tag_list(result.get("missing_skills", []))
 
    with tab_swot:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("💪 Strengths")
            for item in result.get("strengths", []):
                st.markdown(f"- {item}")
        with col_b:
            st.subheader("⚠️ Weaknesses")
            for item in result.get("weaknesses", []):
                st.markdown(f"- {item}")
 
        st.subheader("🛠️ Improvement Suggestions")
        for item in result.get("improvement_suggestions", []):
            st.markdown(f"- {item}")
 
    with tab_growth:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📜 Recommended Certifications")
            for item in result.get("recommended_certifications", []):
                st.markdown(f"- {item}")
            st.subheader("💻 Technologies to Learn")
            render_tag_list(result.get("technologies_to_learn", []))
        with col_b:
            st.subheader("🏗️ Suggested Projects")
            for item in result.get("suggested_projects", []):
                st.markdown(f"- {item}")
            st.subheader("🎯 Recommended Roles")
            render_tag_list(result.get("recommended_roles", []))
 
    with tab_prep:
        st.subheader("Likely Interview Questions")
        for i, question in enumerate(result.get("interview_questions", []), start=1):
            st.markdown(f"**{i}.** {question}")
 
    st.divider()
 
    report_text = build_text_report(result, filename or "resume")
    st.download_button(
        label="⬇️ Download Report (.txt)",
        data=report_text,
        file_name=f"{(filename or 'resume').rsplit('.', 1)[0]}_analysis_report.txt",
        mime="text/plain",
        use_container_width=False,
    )
 