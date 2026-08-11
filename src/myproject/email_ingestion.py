import re
import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
from myproject.data_loader import get_supabase_client, is_valid_supabase_config

STATUS_PATTERNS = {
    "Interviewing": [
        r"schedule\s+(an?\s+)?interview",
        r"invitation\s+to\s+interview",
        r"invite\s+you\s+to\s+interview",
        r"phone\s+screen",
        r"technical\s+interview",
        r"next\s+steps\s+in\s+our\s+hiring\s+process",
        r"like\s+to\s+speak\s+with\s+you",
        r"interview\s+confirmation"
    ],
    "Offer": [
        r"pleased\s+to\s+offer",
        r"offer\s+of\s+employment",
        r"job\s+offer",
        r"congratulations.*offer",
        r"extend\s+an\s+offer"
    ],
    "Rejected": [
        r"decided\s+to\s+move\s+forward\s+with\s+other",
        r"regret\s+to\s+inform",
        r"not\s+selected",
        r"pursuing\s+other\s+candidates",
        r"will\s+not\s+be\s+moving\s+forward",
        r"unfortunately",
        r"position\s+has\s+been\s+filled"
    ],
    "Applied": [
        r"application\s+received",
        r"thank\s+you\s+for\s+applying",
        r"received\s+your\s+application",
        r"application\s+submitted"
    ]
}

KNOWN_COMPANIES = [
    "TechCorp Solutions", "DataFlow Inc", "Innovate Analytics", "CloudNative Systems",
    "Google", "Meta", "Amazon", "Apple", "Microsoft", "Netflix", "Uber", "Airbnb",
    "Stripe", "Snowflake", "Databricks", "Scale AI", "OpenAI", "Anthropic", "Supabase"
]

def parse_job_email(email_text: str, subject: str = "", sender: str = "") -> Dict:
    """
    Parses email text and subject to identify company, target job, detected status, and confidence score.
    """
    combined_content = f"{subject}\n{email_text}".lower()
    
    # 1. Detect Status
    detected_status = "Unknown"
    confidence = 0.0
    
    for status, patterns in STATUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, combined_content, re.IGNORECASE):
                detected_status = status
                # High confidence for explicit subject/body matches
                confidence = 95.0 if status in ["Interviewing", "Offer"] else 88.0
                break
        if detected_status != "Unknown":
            break
            
    if detected_status == "Unknown":
        detected_status = "Applied"
        confidence = 40.0

    # 2. Detect Company
    detected_company = "Unknown"
    
    # Check KNOWN_COMPANIES first
    for comp in KNOWN_COMPANIES:
        if re.search(r'\b' + re.escape(comp) + r'\b', f"{subject} {email_text}", re.IGNORECASE):
            detected_company = comp
            break
            
    if detected_company == "Unknown" and subject:
        # Extract company from subject e.g. "at TechCorp" or "- TechCorp"
        match = re.search(r'(?:at|-)\s+([A-Z][a-zA-Z0-9\s]+)', subject)
        if match:
            detected_company = match.group(1).strip()

    # Fallback to sender domain if still unknown
    if detected_company == "Unknown" and sender and "@" in sender:
        domain = sender.split("@")[-1].split(".")[0].capitalize()
        if domain.lower() not in ["gmail", "yahoo", "hotmail", "outlook", "icloud"]:
            detected_company = domain

    # 3. Detect Role/Job Title
    detected_role = "Software Engineer"
    role_match = re.search(r'(senior|staff|lead|principal)?\s*(software engineer|ai engineer|full stack|data scientist|backend engineer|frontend engineer|ml engineer|product manager)', combined_content)
    if role_match:
        detected_role = role_match.group(0).title()

    return {
        "detected_status": detected_status,
        "detected_company": detected_company,
        "detected_role": detected_role,
        "confidence": confidence,
        "parsed_at": datetime.datetime.now().isoformat(),
        "summary": f"Detected {detected_status} from {detected_company} for {detected_role} role ({confidence}% confidence)."
    }

def process_email_webhook_payload(payload: Dict) -> Tuple[bool, str, Dict]:
    """
    Process incoming webhook payload containing email subject, body, and sender.
    Syncs result to Supabase if connected.
    """
    subject = payload.get("subject", "")
    body = payload.get("body", payload.get("text", ""))
    sender = payload.get("sender", payload.get("from", ""))

    parsed = parse_job_email(body, subject=subject, sender=sender)
    
    is_valid, _ = is_valid_supabase_config()
    if is_valid:
        client = get_supabase_client()
        if client:
            try:
                # Find matching job
                response = client.table('jobs').select('*').ilike('company', f"%{parsed['detected_company']}%").execute()
                jobs = response.data or []
                
                if jobs:
                    target_job = jobs[0]
                    client.table('jobs').update({
                        'status': parsed['detected_status']
                    }).eq('id', target_job['id']).execute()
                    
                    # Log event
                    client.table('job_application_events').insert({
                        'application_id': target_job['id'],
                        'event_type': parsed['detected_status'],
                        'event_date': datetime.datetime.now().isoformat()
                    }).execute()
                    
                    return True, f"✅ Updated existing job #{target_job['id']} ({target_job['company']}) status to {parsed['detected_status']}.", parsed
                else:
                    # Insert new job record
                    client.table('jobs').insert({
                        'company': parsed['detected_company'],
                        'job_title': parsed['detected_role'],
                        'status': parsed['detected_status'],
                        'match_score': 80.0
                    }).execute()
            except Exception as e:
                return True, f"✅ Processed email ({parsed['summary']}) [Database update skipped: {str(e)}]", parsed

    return True, f"✅ Processed payload (Demo mode): {parsed['summary']}", parsed

