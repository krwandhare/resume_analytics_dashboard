import pytest
import io
import PyPDF2
import docx
from myproject.resume_scorer import (
    extract_keywords_from_text,
    calculate_resume_match_score,
    extract_text_from_pdf,
    extract_text_from_docx
)

def test_extract_keywords_from_text():
    sample_text = "I am a Senior Software Engineer skilled in Python, Supabase, PostgreSQL, Docker, and React."
    keywords = extract_keywords_from_text(sample_text)
    
    assert "python" in keywords
    assert "supabase" in keywords
    assert "postgresql" in keywords
    assert "docker" in keywords
    assert "react" in keywords

def test_calculate_resume_match_score_empty():
    res = calculate_resume_match_score("", "Python developer job")
    assert res["score"] == 0.0
    assert res["status"] == "empty_resume"

    res2 = calculate_resume_match_score("Python resume", "")
    assert res2["score"] == 0.0
    assert res2["status"] == "empty_jd"

def test_calculate_resume_match_score_high_match():
    resume = "Experienced Python developer with expertise in Supabase, PostgreSQL, Docker, AWS, and Streamlit."
    jd = "Seeking a Python developer with experience in Supabase, PostgreSQL, Docker, and AWS."
    
    res = calculate_resume_match_score(resume, jd)
    assert res["score"] >= 80.0
    assert "Python" in res["matched_skills"]
    assert "Docker" in res["matched_skills"]
    assert res["status"] == "success"

def test_calculate_resume_match_score_partial_match():
    resume = "Frontend engineer specializing in React, HTML, CSS, JavaScript."
    jd = "Backend engineer required with skills in Python, PostgreSQL, Docker, AWS, React, Kubernetes."
    
    res = calculate_resume_match_score(resume, jd)
    assert res["score"] < 80.0
    assert "React" in res["matched_skills"]
    assert "Python" in res["missing_skills"]
    assert "Docker" in res["missing_skills"]

def test_extract_text_from_pdf():
    # Generate a simple in-memory PDF
    writer = PyPDF2.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    # Should not raise exception
    text = extract_text_from_pdf(pdf_bytes)
    assert isinstance(text, str)

def test_extract_text_from_docx():
    # Generate a simple in-memory DOCX
    doc = docx.Document()
    doc.add_paragraph("Python Developer Resume")
    docx_bytes = io.BytesIO()
    doc.save(docx_bytes)
    docx_bytes.seek(0)

    text = extract_text_from_docx(docx_bytes)
    assert "Python Developer Resume" in text
