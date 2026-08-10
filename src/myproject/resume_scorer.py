import re
from typing import Dict, List, Set, Tuple
import PyPDF2
import docx

# Comprehensive Tech & Domain Keywords Taxonomy
KNOWN_KEYWORDS = {
    # Core Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust", "ruby", "php", "sql", "html", "css", "r", "swift", "kotlin",
    # Frameworks & Libraries
    "react", "next.js", "angular", "vue", "node.js", "express", "django", "flask", "fastapi", "streamlit", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "spring boot", ".net",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform", "ansible", "jenkins", "github actions", "ci/cd", "linux", "bash", "serverless", "lambda",
    # Databases & Storage
    "postgresql", "postgres", "mysql", "mongodb", "redis", "supabase", "firebase", "sqlite", "elasticsearch", "snowflake", "bigquery", "redshift",
    # Data & Analytics
    "data analytics", "data analysis", "data engineering", "etl", "machine learning", "ai", "artificial intelligence", "deep learning", "nlp", "tableau", "power bi", "plotly", "bi", "data visualization",
    # Architecture & Concepts
    "rest", "rest api", "graphql", "microservices", "agile", "scrum", "git", "oop", "system design", "test-driven development", "tdd", "unit testing", "integration testing",
    # Soft Skills & Leadership
    "leadership", "project management", "communication", "problem solving", "collaboration", "cross-functional", "stakeholder management"
}

def extract_text_from_pdf(file) -> str:
    """Extract clean text content from an uploaded PDF file or file stream."""
    try:
        reader = PyPDF2.PdfReader(file)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF file: {str(e)}")

def extract_text_from_docx(file) -> str:
    """Extract clean text content from an uploaded DOCX file or file stream."""
    try:
        doc = docx.Document(file)
        text_parts = [para.text for para in doc.paragraphs if para.text]
        return "\n".join(text_parts).strip()
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX file: {str(e)}")

def extract_keywords_from_text(text: str) -> Set[str]:
    """Extract known technical and domain keywords from given text."""
    if not text or not text.strip():
        return set()
        
    text_lower = text.lower()
    found_keywords = set()
    
    # Check multi-word and single-word keywords
    for keyword in KNOWN_KEYWORDS:
        # Use word boundary matching for accurate keyword extraction
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            found_keywords.add(keyword)
            
    # Also extract general capitalized/technical terms dynamically
    words = re.findall(r'\b[a-zA-Z0-9_\-\+\#]{2,}\b', text)
    for word in words:
        w_lower = word.lower()
        if w_lower in KNOWN_KEYWORDS:
            found_keywords.add(w_lower)
            
    return found_keywords

def calculate_resume_match_score(resume_text: str, job_description: str) -> Dict:
    """
    Calculate ATS match score between resume text and job description.
    Returns dictionary with overall score, matched skills, missing skills, and recommendations.
    """
    if not resume_text or not resume_text.strip():
        return {
            "score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "recommendations": ["Upload or paste your resume text to compute match score."],
            "status": "empty_resume"
        }
        
    if not job_description or not job_description.strip():
        return {
            "score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "recommendations": ["Provide a target job description to compute match score."],
            "status": "empty_jd"
        }

    resume_keywords = extract_keywords_from_text(resume_text)
    jd_keywords = extract_keywords_from_text(job_description)
    
    if not jd_keywords:
        # Fallback keyword extraction from general words in job description
        words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower()))
        stopwords = {"and", "the", "for", "with", "you", "will", "our", "are", "this", "that", "from", "have", "been", "work", "team", "your", "role", "must"}
        jd_keywords = set(w for w in words if w not in stopwords)[:20]

    if not jd_keywords:
        return {
            "score": 50.0,
            "matched_skills": list(resume_keywords),
            "missing_skills": [],
            "recommendations": ["Job description did not contain detectable technical keywords."],
            "status": "no_jd_keywords"
        }

    matched_skills = sorted(list(resume_keywords.intersection(jd_keywords)))
    missing_skills = sorted(list(jd_keywords - resume_keywords))
    
    match_ratio = len(matched_skills) / len(jd_keywords) if jd_keywords else 0.0
    score = round(match_ratio * 100, 1)

    recommendations = []
    if missing_skills:
        top_missing = ", ".join([f"**{s.title()}**" for s in missing_skills[:5]])
        recommendations.append(f"🎯 Add missing key skills to your resume: {top_missing}.")
        
    if score >= 80:
        recommendations.append("🌟 Excellent match! Your resume contains the core qualifications listed in the job description.")
    elif score >= 50:
        recommendations.append("📈 Moderate match. Emphasize your experience with missing skills in your resume summary or bullet points.")
    else:
        recommendations.append("⚠️ Low ATS match. Consider tailoring your experience descriptions to directly incorporate target job keywords.")

    return {
        "score": min(score, 100.0),
        "matched_skills": [s.title() for s in matched_skills],
        "missing_skills": [s.title() for s in missing_skills],
        "recommendations": recommendations,
        "total_jd_keywords": len(jd_keywords),
        "status": "success"
    }
