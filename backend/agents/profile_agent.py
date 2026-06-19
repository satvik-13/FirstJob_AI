"""
Profile Agent
-------------
Parses uploaded resumes (PDF/DOCX) into a structured JSON profile.
This profile is the immutable source of truth for all downstream agents.

Responsibilities:
- Extract raw text from PDF or DOCX
- Use the LLM to parse into structured JSON
- Validate and store the profile
- Never modify after initial creation (only replace on re-upload)
"""

import pdfplumber
import docx
import json
import re
from pathlib import Path
from core.config import settings
from loguru import logger
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=settings.anthropic_api_key,
    base_url="https://api.aimlapi.com/v1",
)

PROFILE_SYSTEM_PROMPT = """You are an expert resume parser. Your job is to extract structured information from resume text with high accuracy.

CRITICAL RULES:
1. Only extract information that is EXPLICITLY present in the resume text
2. Never invent, infer, or assume information that isn't there
3. If a field is not found, use null — do not guess
4. Preserve the exact wording of bullet points — do not paraphrase
5. Extract ALL skills mentioned anywhere in the resume
6. For experience bullets, keep them verbatim from the resume

Output ONLY valid JSON matching this exact schema, no preamble, no markdown:
{
  "full_name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "location": "string or null",
  "summary": "string or null",
  "skills": ["skill1", "skill2"],
  "experience": [
    {
      "company": "string",
      "title": "string",
      "start_date": "string or null",
      "end_date": "string or null",
      "duration": "string or null",
      "location": "string or null",
      "bullets": ["exact bullet point 1", "exact bullet point 2"]
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string or null",
      "field": "string or null",
      "year": "string or null",
      "gpa": "string or null"
    }
  ],
  "projects": [
    {
      "name": "string",
      "description": "string or null",
      "tech_stack": ["tech1", "tech2"],
      "bullets": ["bullet1"]
    }
  ],
  "certifications": ["cert1"],
  "languages": ["language1"],
  "links": {
    "linkedin": "url or null",
    "github": "url or null",
    "portfolio": "url or null"
  }
}"""


def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from PDF using pdfplumber."""
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def extract_text_from_docx(file_path: str) -> str:
    """Extract raw text from DOCX."""
    doc = docx.Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)


def extract_resume_text(file_path: str) -> str:
    """Extract text from PDF or DOCX based on file extension."""
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Only PDF and DOCX are supported.")

    if not text.strip():
        raise ValueError("Could not extract text from the resume. The file may be image-based or corrupted.")

    return text


async def parse_resume_with_ai(raw_text: str) -> dict:
    """
    Use the LLM to parse raw resume text into structured JSON.
    This is the core intelligence of the Profile Agent.
    """
    logger.info("Parsing resume with AI...")

    response = await client.chat.completions.create(
        model="claude-haiku-4-5",  # Fast and cheap for parsing
        max_tokens=4096,
        messages=[
            {"role": "system", "content": PROFILE_SYSTEM_PROMPT},
            {"role": "user", "content": f"Parse this resume into the JSON schema:\n\n{raw_text}"}
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    raw_output = re.sub(r'^```json\s*', '', raw_output)
    raw_output = re.sub(r'^```\s*', '', raw_output)
    raw_output = re.sub(r'\s*```$', '', raw_output)

    parsed = json.loads(raw_output)
    logger.info(f"Resume parsed successfully. Found {len(parsed.get('skills', []))} skills, "
                f"{len(parsed.get('experience', []))} experience entries.")
    return parsed


async def process_resume_upload(file_path: str, original_filename: str) -> dict:
    """
    Full pipeline: file → raw text → structured profile.
    Returns a dict with raw_text and parsed_profile.
    """
    logger.info(f"Processing resume: {original_filename}")

    # Step 1: Extract raw text
    raw_text = extract_resume_text(file_path)
    logger.info(f"Extracted {len(raw_text)} characters from resume")

    # Step 2: Parse with AI
    parsed_profile = await parse_resume_with_ai(raw_text)

    return {
        "raw_text": raw_text,
        "parsed_profile": parsed_profile,
        "original_filename": original_filename,
    }