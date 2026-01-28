"""
CV Scoring Service - Automatically analyzes CVs and LinkedIn profiles 
to generate candidate scores against job requirements.
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

_client: Optional[OpenAI] = None


def _build_openai_client() -> Optional[OpenAI]:
    """Construct a client only when credentials are present."""
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
    if not api_key:
        logger.warning("OpenAI API key missing; CV scoring disabled.")
        return None

    return OpenAI(
        api_key=api_key,
        base_url=os.environ.get("OPENAI_BASE_URL") or os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL"),
    )

async def analyze_cv(
    cv_text: str,
    job_title: str,
    job_description: str,
    required_skills: list[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Analyze CV text against job requirements and return scoring.
    
    Returns:
        Dict with cv_scoring, skills_match_score, education_level, 
        years_experience, current_position or None when disabled/failed.
    """
    required_skills = required_skills or []
    skills_list = ", ".join(required_skills) if required_skills else "Not specified"
    
    prompt = f"""Analyze this CV/resume against the job requirements and provide a JSON response.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_description[:2000]}

REQUIRED SKILLS: {skills_list}

CV/RESUME TEXT:
{cv_text[:4000]}

Provide a JSON response with these exact fields:
{{
    "cv_scoring": <integer 0-100, overall match percentage based on qualifications, experience, and fit>,
    "skills_match_score": <integer 0-100, how well candidate's skills match required skills>,
    "education_level": "<one of: PhD, Master's Degree, Bachelor's Degree, Diploma, High School, or Not Specified>",
    "years_experience": <integer, estimated years of relevant experience>,
    "current_position": "<current or most recent job title>",
    "key_strengths": ["<strength1>", "<strength2>", "<strength3>"],
    "areas_of_concern": ["<concern1>", "<concern2>"]
}}

Be accurate and fair in scoring. A score of 80+ indicates excellent match, 60-79 good match, 40-59 moderate match, below 40 poor match.
Return ONLY valid JSON, no additional text."""

    global _client
    client = _client or _build_openai_client()
    _client = client
    if client is None:
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert HR recruiter analyzing CVs. Provide accurate, unbiased assessments in JSON format only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean up response (remove markdown if present)
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        result_text = result_text.strip()
        
        result = json.loads(result_text)
        
        # Validate and normalize values
        return {
            "cv_scoring": max(0, min(100, int(result.get("cv_scoring", 0)))),
            "skills_match_score": max(0, min(100, int(result.get("skills_match_score", 0)))),
            "education_level": result.get("education_level", "Not Specified"),
            "years_experience": max(0, int(result.get("years_experience", 0))),
            "current_position": result.get("current_position", ""),
            "key_strengths": result.get("key_strengths", []),
            "areas_of_concern": result.get("areas_of_concern", [])
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse CV analysis response: {e}")
        return None
    except Exception as e:
        logger.error(f"CV analysis failed: {e}")
        return None


async def extract_text_from_pdf(pdf_content: bytes) -> Optional[str]:
    """Extract text from PDF content."""
    try:
        import io
        # Try using pdfplumber if available
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except ImportError:
            pass
        
        # Fallback to PyPDF2
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except ImportError:
            pass
            
        logger.warning("No PDF library available for text extraction")
        return None
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return None


async def extract_text_from_docx(docx_content: bytes) -> Optional[str]:
    """Extract text from DOCX content."""
    try:
        import io
        from docx import Document
        doc = Document(io.BytesIO(docx_content))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except ImportError:
        logger.warning("python-docx not available for DOCX extraction")
        return None
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        return None


async def score_candidate_cv(
    candidate_id: int,
    cv_content: bytes,
    filename: str,
    job_title: str,
    job_description: str,
    required_skills: list[str] = None,
    db_session = None
) -> Optional[Dict[str, Any]]:
    """
    Score a candidate's CV and update their record.
    
    Args:
        candidate_id: ID of the candidate
        cv_content: Raw file content
        filename: Original filename (for determining type)
        job_title: Position title
        job_description: Job description text
        required_skills: List of required skills
        db_session: Database session for updating candidate
    
    Returns:
        Scoring results or None on failure
    """
    # Extract text based on file type
    ext = filename.lower().split('.')[-1]
    
    if ext == 'pdf':
        cv_text = await extract_text_from_pdf(cv_content)
    elif ext in ('docx', 'doc'):
        cv_text = await extract_text_from_docx(cv_content)
    elif ext == 'txt':
        cv_text = cv_content.decode('utf-8', errors='ignore')
    else:
        logger.warning(f"Unsupported file type: {ext}")
        return None
    
    if not cv_text or len(cv_text.strip()) < 50:
        logger.warning("Insufficient text extracted from CV")
        return None
    
    # Analyze the CV
    scores = await analyze_cv(
        cv_text=cv_text,
        job_title=job_title,
        job_description=job_description,
        required_skills=required_skills
    )
    
    if scores and db_session:
        # Update candidate record
        from sqlalchemy import update
        from app.models.recruitment import Candidate
        
        stmt = update(Candidate).where(Candidate.id == candidate_id).values(
            cv_scoring=scores["cv_scoring"],
            skills_match_score=scores["skills_match_score"],
            education_level=scores["education_level"],
            years_experience=scores["years_experience"],
            current_position=scores["current_position"],
            cv_scored_at=datetime.utcnow()
        )
        await db_session.execute(stmt)
        await db_session.commit()
        
        logger.info(f"Updated candidate {candidate_id} with CV scores: {scores['cv_scoring']}%")
    
    return scores
