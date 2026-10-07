"""
server.py

FastAPI Web Backend for the AI Resume Analyzer.
Connects existing core modules (pdf_reader, formatter, analyzer, report)
to a modern, high-performance web interface.
"""

import io
import os
import sys
import webbrowser
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import config
from pdf_reader import extract_text_from_pdf
from utils.formatter import clean_text
from analyzer import run_full_analysis, AIProviderError, ResponseParsingError, ResumeAnalysisError
from report import generate_pdf_report, build_text_report

app = FastAPI(
    title="AI Resume Analyzer API",
    description="Backend API for AI-powered resume parsing and ATS scoring",
    version="1.0.0",
)

# Ensure static directory exists
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

if (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>AI Resume Analyzer Backend Running</h1>")


@app.get("/api/config")
async def get_app_config():
    """Returns application configuration metadata."""
    has_key = bool(
        (config.AI_PROVIDER == "gemini" and config.GEMINI_API_KEY)
        or (config.AI_PROVIDER == "openai" and config.OPENAI_API_KEY)
    )
    return {
        "provider": config.AI_PROVIDER,
        "model": config.GEMINI_MODEL if config.AI_PROVIDER == "gemini" else config.OPENAI_MODEL,
        "max_file_size_mb": config.MAX_FILE_SIZE_MB,
        "allowed_file_types": config.ALLOWED_FILE_TYPES,
        "has_api_key": has_key,
    }


@app.post("/api/analyze")
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """
    Accepts a PDF resume upload, extracts and cleans text,
    runs full AI + ATS analysis, and returns structured JSON results.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported. Please upload a PDF resume.",
        )

    file_bytes = await file.read()
    file_size_mb = len(file_bytes) / (1024 * 1024)

    if file_size_mb > config.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size_mb:.1f} MB) exceeds maximum allowed limit of {config.MAX_FILE_SIZE_MB} MB.",
        )

    pdf_stream = io.BytesIO(file_bytes)

    try:
        raw_text = extract_text_from_pdf(pdf_stream)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF file: {str(e)}",
        )

    if not raw_text or not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from this PDF. It may be scanned images or corrupted. Please try a text-based PDF.",
        )

    cleaned_text = clean_text(raw_text)

    if len(cleaned_text) < 50:
        # Very short text warning handled gracefully
        pass

    try:
        result = run_full_analysis(cleaned_text)
        return {
            "status": "success",
            "filename": file.filename,
            "result": result,
            "text_length": len(cleaned_text),
        }
    except AIProviderError as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI Service error: {str(e)}. Please check your network connection and API keys.",
        )
    except ResponseParsingError as e:
        raise HTTPException(
            status_code=500,
            detail="The AI provider returned an unrecognized response format. Please try again.",
        )
    except ResumeAnalysisError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during analysis: {str(e)}",
        )


@app.post("/api/download/pdf")
async def download_pdf_report(payload: dict):
    """Generates and streams downloadable PDF report."""
    result = payload.get("result")
    filename = payload.get("filename", "resume.pdf")

    if not result:
        raise HTTPException(status_code=400, detail="Analysis result object is required.")

    pdf_bytes = generate_pdf_report(result, filename)
    clean_name = filename.rsplit(".", 1)[0]
    out_name = f"{clean_name}_analysis_report.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )


@app.post("/api/download/text")
async def download_text_report(payload: dict):
    """Generates and streams downloadable plain text report."""
    result = payload.get("result")
    filename = payload.get("filename", "resume.pdf")

    if not result:
        raise HTTPException(status_code=400, detail="Analysis result object is required.")

    text_report = build_text_report(result, filename)
    clean_name = filename.rsplit(".", 1)[0]
    out_name = f"{clean_name}_analysis_report.txt"

    return Response(
        content=text_report,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )


def start():
    """Launches uvicorn server and opens browser."""
    import uvicorn
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    print("\n" + "=" * 60)
    print(f"  🚀 AI Resume Analyzer is running at: {url}")
    print("=" * 60 + "\n")

    webbrowser.open(url)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start()
