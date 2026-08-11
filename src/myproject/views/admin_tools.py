import streamlit as st
import pandas as pd
from myproject.components.email_webhook_ingestion import render_email_webhook_ingestion
from myproject.components.data_manager import render_data_manager

def render_admin_tools_view(job_data: pd.DataFrame, apps_df: pd.DataFrame = None, events_df: pd.DataFrame = None) -> None:
    """Render the Admin & Tools tab view."""
    st.markdown("## ⚙️ Admin Tools & Database Management")
    st.caption("Test automated email status parsing, configure incoming webhooks, and manage database records.")

    # Email Status Ingestion & Webhook Alerts
    render_email_webhook_ingestion(job_data)

    st.divider()

    # Supabase Table Data Manager & Migration Tools
    render_data_manager(job_data, apps_df if apps_df is not None else pd.DataFrame(), events_df if events_df is not None else pd.DataFrame())
