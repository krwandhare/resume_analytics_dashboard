import streamlit as st
import pandas as pd
from myproject.email_ingestion import parse_job_email, process_email_webhook_payload

SAMPLE_EMAILS = {
    "🎉 Interview Invitation": {
        "sender": "recruiting@techcorp.com",
        "subject": "Interview Invitation - Senior AI Engineer at TechCorp Solutions",
        "body": "Hi there,\n\nThank you for your interest in the Senior AI Engineer position at TechCorp Solutions. We were very impressed by your resume and would like to invite you to a 45-minute technical interview with our engineering lead next week.\n\nPlease let us know your availability.\n\nBest regards,\nTechCorp Recruiting Team"
    },
    "✉️ Rejection Notice": {
        "sender": "careers@innovateanalytics.io",
        "subject": "Update on your Data Scientist application at Innovate Analytics",
        "body": "Dear Applicant,\n\nThank you for taking the time to apply for the Data Scientist role at Innovate Analytics. After careful consideration, we have decided to move forward with other candidates whose qualifications more closely align with our current needs.\n\nWe wish you the best in your job search.\n\nBest,\nInnovate Talent Team"
    },
    "🏆 Job Offer Letter": {
        "sender": "hr@cloudnative.io",
        "subject": "Offer of Employment - CloudNative Systems",
        "body": "Congratulations!\n\nWe are pleased to offer you the position of Backend Engineer at CloudNative Systems. Attached you will find your official offer letter detailing salary, benefits, and start date.\n\nPlease review and let us know if you have any questions.\n\nWarmly,\nCloudNative HR"
    },
    "📩 Application Received": {
        "sender": "jobs@dataflow.com",
        "subject": "Application Received: Full Stack Developer",
        "body": "Hi,\n\nWe have received your application for the Full Stack Developer role at DataFlow Inc. Our team will review your qualifications and reach out if there is a fit.\n\nThanks,\nDataFlow Recruiting"
    }
}

def render_email_webhook_ingestion(job_data: pd.DataFrame) -> None:
    """Render the Automated Email Status Ingestion & Webhook Alerts component."""
    st.subheader("📬 Automated Email Status Ingestion & Webhook Alerts")
    st.caption("Automatically ingest application emails (Gmail, Greenhouse, Lever) or receive incoming webhooks to update job statuses in real-time.")

    tab1, tab2 = st.tabs(["📧 Interactive Email Parser", "🔗 Webhook Integration Setup"])

    with tab1:
        st.markdown("### Test Email Parser & Auto Status Updater")
        st.caption("Select a preset sample email or paste raw email contents below to test automated parsing.")

        preset_choice = st.selectbox("Quick Load Sample Email", list(SAMPLE_EMAILS.keys()))
        selected_sample = SAMPLE_EMAILS[preset_choice]

        with st.form(key="email_parser_form"):
            sender_input = st.text_input("Sender Email Address", value=selected_sample["sender"])
            subject_input = st.text_input("Email Subject Line", value=selected_sample["subject"])
            body_input = st.text_area("Email Content Body", value=selected_sample["body"], height=180)

            submit_parse = st.form_submit_button("⚡ Process & Update Status", type="primary")

        if submit_parse:
            if not body_input.strip():
                st.error("Please enter email body content to parse.")
            else:
                payload = {
                    "sender": sender_input,
                    "subject": subject_input,
                    "body": body_input
                }
                success, message, parsed_info = process_email_webhook_payload(payload)

                st.markdown("---")
                st.markdown("### 📊 Email Parsing Results")

                pcol1, pcol2, pcol3, pcol4 = st.columns(4)
                with pcol1:
                    st.metric("Detected Status", parsed_info["detected_status"])
                with pcol2:
                    st.metric("Detected Company", parsed_info["detected_company"])
                with pcol3:
                    st.metric("Detected Role", parsed_info["detected_role"])
                with pcol4:
                    st.metric("Parsing Confidence", f"{parsed_info['confidence']}%")

                if success:
                    st.success(message)
                    st.toast(f"✅ Status updated to {parsed_info['detected_status']}!")
                else:
                    st.warning(message)

    with tab2:
        st.markdown("### 🔗 Incoming Webhook Configuration")
        st.markdown("""
        You can connect **n8n**, **Zapier**, **Make.com**, or **SendGrid Inbound Parse** to post email notifications directly to your dashboard.
        """)

        st.markdown("#### Sample Webhook Payload (POST /api/webhook/email)")
        st.code("""
{
  "sender": "recruiting@company.com",
  "subject": "Interview Invitation - Senior Engineer",
  "body": "We would like to invite you for a technical interview...",
  "timestamp": "2026-08-10T16:55:00Z"
}
        """, language="json")

        st.markdown("#### Test with cURL command")
        st.code("""
curl -X POST "http://localhost:8501/api/webhook/email" \\
     -H "Content-Type: application/json" \\
     -d '{
       "sender": "recruiting@google.com",
       "subject": "Invitation to Interview at Google",
       "body": "We invite you to phone screen next week."
     }'
        """, language="bash")
