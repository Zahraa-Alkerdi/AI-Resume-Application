#!/usr/bin/env python
import sys
import warnings
from urllib.parse import urlparse
import json, re

from crew import MyCrewai
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

from schemas import ATSOptimizationSchema

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = FastAPI()


# ---------------------------
# HELPERS
# ---------------------------
def extract_github_username(github_url: str) -> str:
    if not github_url:
        return ""

    parsed_url = urlparse(github_url.strip())
    parts = parsed_url.path.strip("/").split("/")

    return parts[0] if parts and parts[0] else ""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


# ---------------------------
# STRICT JSON PARSER
# ---------------------------
def safe_parse_json(text):
    if isinstance(text, dict):
        return text

    if not isinstance(text, str):
        return {"raw_output": str(text)}

    text = text.strip().replace("```json", "").replace("```", "")

    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

    return {"raw_output": text}


# ---------------------------
# ENDPOINT
# ---------------------------
@app.post("/process-resume")
async def process_resume(
    resume: UploadFile = File(...),
    cover_letter: UploadFile = File(...),
    job_requirements: str = Form(...),
    github_url: str | None = Form(None)
):

    resume_bytes = await resume.read()
    cover_bytes = await cover_letter.read()

    if not resume_bytes:
        raise HTTPException(400, "Empty resume file")

    if not cover_bytes:
        raise HTTPException(400, "Empty cover letter file")

    github_username = extract_github_username(github_url) if github_url else ""

    # ---------------------------
    # Parse files
    # ---------------------------
    if resume.content_type == "application/pdf":
        resume_text = extract_text_from_pdf(resume_bytes)
    else:
        resume_text = extract_text_from_docx(resume_bytes)

    if cover_letter.content_type == "application/pdf":
        cover_text = extract_text_from_pdf(cover_bytes)
    else:
        cover_text = extract_text_from_docx(cover_bytes)

    # ---------------------------
    # CrewAI inputs
    # ---------------------------
    inputs = {
        "resume": resume_text,
        "cover_letter": cover_text,
        "job_requirements": job_requirements,
        "github_username": github_username,
        "has_github": bool(github_username)
    }

    crew_instance = MyCrewai()
    crew_instance.has_github = bool(github_username)
    crew = crew_instance.crew()

    try:
        result = crew.kickoff(inputs=inputs)
    except Exception as e:
        raise HTTPException(500, f"Crew execution failed: {str(e)}")

    tasks_output = getattr(result, "tasks_output", None)

    if not tasks_output:
        raise HTTPException(500, "Empty CrewAI output")

    response = {}

    for task_output in tasks_output:
        parsed = safe_parse_json(task_output.raw)

        # ---------------------------
        # ATS SCHEMA VALIDATION (IMPORTANT FIX)
        # ---------------------------
        if task_output.name == "ats_optimization_task":
            try:
                parsed = ATSOptimizationSchema.model_validate(parsed).model_dump()
            except Exception:
                parsed = {
                    "ats_resume": "",
                    "ats_cover_letter": "",
                    "keywords_used": [],
                    "formatting_notes": []
                }

        response[task_output.name] = parsed if parsed else {}
    
    final_response = {
        "analysis": response.get("analysis", {}),
        "editing": response.get("editing", {}),
        "ats_optimization": response.get("ats_optimization", {}),
        "review": response.get("review", {})
    }

    return {
        "status": "success",
        "data": final_response
    }
