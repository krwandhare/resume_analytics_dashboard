import pandas as pd
import streamlit as st

from myproject.weekly_digest import build_weekly_digest, render_digest_markdown


def _delta_label(value: int) -> str:
    if value > 0:
        return f"+{value} vs prior week"
    return f"{value} vs prior week"


def render_weekly_digest_view(
    job_data: pd.DataFrame,
    apps_df: pd.DataFrame | None = None,
    events_df: pd.DataFrame | None = None,
) -> None:
    """Render the weekly analytics summary and portable digest download."""
    st.markdown("## :material/calendar_view_week: Weekly digest")
    st.caption("A Monday-to-Monday UTC summary of application and pipeline activity.")

    digest = build_weekly_digest(job_data, apps_df, events_df)
    markdown = render_digest_markdown(digest)

    with st.container(horizontal=True):
        st.metric(
            "Applications",
            digest.applications,
            _delta_label(digest.application_delta),
            border=True,
        )
        st.metric("Status changes", digest.status_changes, border=True)
        st.metric("Interviews", digest.interviews, border=True)
        st.metric("Offers", digest.offers, border=True)

    with st.container(horizontal=True):
        st.metric("Application → interview", f"{digest.interview_rate:.1f}%", border=True)
        st.metric("Interview → offer", f"{digest.offer_rate:.1f}%", border=True)

    with st.container(border=True):
        st.subheader("Top companies")
        if digest.top_companies:
            company_df = pd.DataFrame(digest.top_companies, columns=["Company", "Applications"])
            st.bar_chart(company_df, x="Company", y="Applications")
        else:
            st.info("No applications were recorded in the current weekly window.")

    with st.expander("Digest preview", expanded=True):
        st.markdown(markdown)

    st.download_button(
        "Download Markdown digest",
        data=markdown,
        file_name=f"weekly-job-digest-{digest.week_start:%Y-%m-%d}.md",
        mime="text/markdown",
        icon=":material/download:",
    )

    st.caption(
        "Automated email delivery is available through the repository's weekly workflow "
        "after SMTP and Supabase secrets are configured."
    )
