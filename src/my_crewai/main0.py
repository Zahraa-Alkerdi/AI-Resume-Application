#!/usr/bin/env python
import sys
import warnings

from my_crewai.backend.crew import MyCrewai
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = FastAPI()

# ---------------------------
# PDF PARSER
# ---------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


# ---------------------------
# DOCX PARSER
# ---------------------------
def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


# ---------------------------
# MAIN ENDPOINT
# ---------------------------
@app.post("/process-resume")
async def process_resume(
    resume: UploadFile = File(...),
    cover_letter: UploadFile = File(...),
    job_requirements: str = Form(...)
):

    # Read files
    resume_bytes = await resume.read()
    cover_bytes = await cover_letter.read()

    # Basic validation
    if not resume_bytes:
        raise HTTPException(status_code=400, detail="Empty resume file")

    if not cover_bytes:
        raise HTTPException(status_code=400, detail="Empty cover letter file")

    # ---------------------------
    # Resume parsing
    # ---------------------------
    if resume.content_type == "application/pdf":
        resume_text = extract_text_from_pdf(resume_bytes)

    elif resume.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = extract_text_from_docx(resume_bytes)

    else:
        raise HTTPException(status_code=400, detail="Unsupported resume format")

    # ---------------------------
    # Cover letter parsing
    # ---------------------------
    if cover_letter.content_type == "application/pdf":
        cover_text = extract_text_from_pdf(cover_bytes)

    elif cover_letter.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        cover_text = extract_text_from_docx(cover_bytes)

    else:
        raise HTTPException(status_code=400, detail="Unsupported cover letter format")

    # ---------------------------
    # CrewAI input
    # ---------------------------
    inputs = {
        "resume": resume_text,
        "cover_letter": cover_text,
        "job_requirements": job_requirements
    }

    # Run crew
    result = MyCrewai().crew().kickoff(inputs=inputs)

    # Return structured response
    return {
        "status": "success",
        "result": result
    }
    


def run():
    inputs = inputs

    try:
        MyCrewai().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

