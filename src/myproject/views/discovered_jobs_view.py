import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_myproject_dir = os.path.dirname(_this_dir)
_src_dir = os.path.dirname(_myproject_dir)

for _p in [_src_dir, _myproject_dir, _this_dir]:
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    from myproject.data_loader import (
        add_discovered_to_tracker,
        dismiss_discovered_jobs,
        format_staleness,
    )
    from myproject.resume_scorer import calculate_resume_match_score
except ImportError:
    from ..data_loader import (
        add_discovered_to_tracker,
        dismiss_discovered_jobs,
        format_staleness,
    )
    from ..resume_scorer import calculate_resume_match_score


# ── Helpers ────────────────────────────────────────────────────────────────────

def _source_badge(source: Optional[str]) -> str:
    src = str(source or "").lower()
    if "gmail" in src:
        return "📧 Gmail"
    if "linkedin" in src:
        return "🔗 LinkedIn"
    if "manual" in src:
        return "✍️ Manual"
    return f"🌐 {source or 'Unknown'}"


def _reason_label(reason: Optional[str]) -> str:
    r = str(reason or "").replace("_", " ").title()
    return r or "—"


def _filter_by_date(df: pd.DataFrame, window: str) -> pd.DataFrame:
    if window == "All" or 'posted_at' not in df.columns:
        return df
    days_map = {"7d": 7, "30d": 30, "90d": 90}
    cutoff = pd.Timestamp.now(tz="UTC") - timedelta(days=days_map[window])
    return df[df['posted_at'].notna() & (df['posted_at'] >= cutoff)]


# ── Main View ──────────────────────────────────────────────────────────────────

def render_discovered_jobs_view(discovered_df: pd.DataFrame) -> None:
    """Render the 🔭 Discovered Jobs tab."""

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("## 🔭 Discovered Jobs")
    st.caption(
        "Jobs found via Gmail alerts and other sources. "
        "Review, tailor your resume, and promote the best ones to your Job Tracker."
    )

    if discovered_df is None or discovered_df.empty:
        st.info(
            "No unresolved discovered jobs found. "
            "All items have been added to the tracker or dismissed, "
            "or Supabase is not connected."
        )
        return

    now_utc = pd.Timestamp.now(tz="UTC")

    # ── KPI Row ───────────────────────────────────────────────────────────────
    total = len(discovered_df)
    today_count = 0
    week_count = 0
    if 'posted_at' in discovered_df.columns:
        cutoff_today = now_utc - timedelta(days=1)
        cutoff_week = now_utc - timedelta(days=7)
        today_count = int((discovered_df['posted_at'] >= cutoff_today).sum())
        week_count = int((discovered_df['posted_at'] >= cutoff_week).sum())

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("🔭 Unresolved", total, help="Total unresolved discovered jobs")
    kpi2.metric("📅 Today", today_count, help="Discovered in the last 24 hours")
    kpi3.metric("📆 This Week", week_count, help="Discovered in the last 7 days")

    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns([2, 1.5, 1.5, 2])
    with fc1:
        keyword = st.text_input(
            "🔍 Keyword Search",
            placeholder="Title or company…",
            key="disc_keyword",
            label_visibility="collapsed",
        )
    with fc2:
        companies = sorted(
            [c for c in discovered_df['company'].dropna().unique() if str(c).strip()]
        )
        company_f = st.multiselect(
            "Company",
            options=companies,
            default=[],
            key="disc_company_f",
            placeholder="All companies",
            label_visibility="collapsed",
        )
    with fc3:
        date_range = st.selectbox(
            "Date Range",
            options=["7d", "30d", "90d", "All"],
            index=1,
            key="disc_date_range",
            label_visibility="collapsed",
        )
    with fc4:
        sort_by = st.selectbox(
            "Sort By",
            options=["Newest First", "Match Score ↓"],
            index=0,
            key="disc_sort_by",
            label_visibility="collapsed",
        )

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = discovered_df.copy()
    filtered = _filter_by_date(filtered, date_range)
    if company_f:
        filtered = filtered[filtered['company'].isin(company_f)]
    if keyword:
        kw = keyword.lower()
        mask = (
            filtered.get('job_title', pd.Series(dtype=str)).astype(str).str.lower().str.contains(kw, na=False)
            | filtered.get('company', pd.Series(dtype=str)).astype(str).str.lower().str.contains(kw, na=False)
        )
        filtered = filtered[mask]
    if sort_by == "Match Score ↓":
        if 'match_score' in filtered.columns:
            filtered = filtered.sort_values('match_score', ascending=False)
    # else stays newest-first (already sorted on load)

    # ── Batch Dismiss ─────────────────────────────────────────────────────────
    st.markdown(f"**Showing {len(filtered)} of {total} unresolved jobs**")

    # Use session state to track selections for batch dismiss
    if 'disc_selected' not in st.session_state:
        st.session_state.disc_selected = set()

    sel_col, bulk_col = st.columns([6, 1])
    with sel_col:
        select_all = st.checkbox(
            "Select all visible",
            key="disc_select_all",
            value=False,
        )
    with bulk_col:
        if st.button(
            "🗑️ Bulk Dismiss",
            type="secondary",
            disabled=not (select_all or st.session_state.disc_selected),
            key="disc_bulk_dismiss",
        ):
            ids_to_dismiss = (
                list(filtered['id'].tolist()) if select_all
                else list(st.session_state.disc_selected)
            )
            ok, msg = dismiss_discovered_jobs(ids_to_dismiss)
            if ok:
                st.success(msg)
                st.session_state.disc_selected = set()
                st.rerun()
            else:
                st.error(msg)

    st.markdown("---")

    if filtered.empty:
        st.info("No jobs match your current filters.")
        return

    # ── Per-Row Cards ─────────────────────────────────────────────────────────
    for _, row in filtered.iterrows():
        row_id = int(row.get('id', 0))
        job_title = str(row.get('job_title') or 'Unknown Title')
        company = str(row.get('company') or 'Unknown Company')
        job_url = str(row.get('job_url') or '')
        source = row.get('source', '')
        reason = row.get('reason', '')
        posted_at = row.get('posted_at')
        staleness = format_staleness(posted_at)

        # Checkbox for batch selection
        checked = st.checkbox(
            label=f"Select **{job_title}** @ {company}",
            value=(row_id in st.session_state.disc_selected or select_all),
            key=f"disc_sel_{row_id}",
            label_visibility="collapsed",
        )
        if checked:
            st.session_state.disc_selected.add(row_id)
        else:
            st.session_state.disc_selected.discard(row_id)

        with st.expander(
            f"{staleness} &nbsp; **{job_title}** &nbsp;›&nbsp; {company}",
            expanded=False,
        ):
            # Meta row
            meta_cols = st.columns([2, 2, 3])
            meta_cols[0].markdown(f"**Source:** {_source_badge(source)}")
            meta_cols[1].markdown(f"**Reason:** `{_reason_label(reason)}`")
            if job_url and job_url.startswith("http"):
                meta_cols[2].markdown(f"[🔗 Open Job Posting]({job_url})")

            st.markdown("---")

            # ── Inline Add-to-Tracker Form ─────────────────────────────────
            with st.form(key=f"disc_add_form_{row_id}", border=False):
                st.markdown("##### ✅ Add to Job Tracker")
                form_c1, form_c2 = st.columns(2)
                with form_c1:
                    f_title = st.text_input(
                        "Job Title",
                        value=job_title,
                        key=f"f_title_{row_id}",
                    )
                    f_company = st.text_input(
                        "Company",
                        value=company,
                        key=f"f_company_{row_id}",
                    )
                with form_c2:
                    f_score = st.slider(
                        "Match Score",
                        min_value=0,
                        max_value=100,
                        value=70,
                        step=5,
                        key=f"f_score_{row_id}",
                        help="Your estimated ATS match score (0-100)",
                    )
                    f_url = st.text_input(
                        "Job URL",
                        value=job_url,
                        key=f"f_url_{row_id}",
                    )
                f_notes = st.text_area(
                    "Notes / Resume Tailoring Tips",
                    placeholder="Add cover letter hints, keywords to include, or interview prep notes…",
                    key=f"f_notes_{row_id}",
                    height=90,
                )
                btn_add, btn_dismiss = st.columns([1, 1])
                submitted_add = btn_add.form_submit_button(
                    "✅ Add to Tracker",
                    type="primary",
                    width="stretch",
                )
                submitted_dismiss = btn_dismiss.form_submit_button(
                    "🗑️ Dismiss",
                    type="secondary",
                    width="stretch",
                )

            if submitted_add:
                ok, msg = add_discovered_to_tracker(
                    queue_id=row_id,
                    job_title=f_title,
                    company=f_company,
                    match_score=f_score,
                    notes=f_notes,
                    job_url=f_url,
                )
                if ok:
                    st.success(msg)
                    st.session_state.disc_selected.discard(row_id)
                    st.rerun()
                else:
                    st.error(msg)

            if submitted_dismiss:
                ok, msg = dismiss_discovered_jobs([row_id])
                if ok:
                    st.success(msg)
                    st.session_state.disc_selected.discard(row_id)
                    st.rerun()
                else:
                    st.error(msg)

            # ── AI Tailor Resume Button ────────────────────────────────────
            if st.button(
                "🎯 Tailor Resume (AI)",
                key=f"disc_tailor_{row_id}",
                type="secondary",
                help="Analyze your resume against this job's description",
            ):
                st.session_state[f'show_tailor_{row_id}'] = True

            if st.session_state.get(f'show_tailor_{row_id}'):
                with st.container(border=True):
                    st.markdown("**🎯 Resume Tailoring Analysis**")
                    resume_text = st.text_area(
                        "Paste your resume text here:",
                        key=f"tailor_resume_{row_id}",
                        height=150,
                        placeholder="Paste the full text of your resume…",
                    )
                    jd_text = st.text_area(
                        "Paste the full job description:",
                        key=f"tailor_jd_{row_id}",
                        height=150,
                        placeholder="Paste the full job description here…",
                    )
                    if st.button("Run Analysis", key=f"run_tailor_{row_id}", type="primary"):
                        if resume_text and jd_text:
                            with st.spinner("Analyzing…"):
                                result = calculate_resume_match_score(resume_text, jd_text)
                            score = result.get('score', 0)
                            matched = result.get('matched_skills', [])
                            missing = result.get('missing_skills', [])
                            recs = result.get('recommendations', [])

                            score_color = (
                                "#22c55e" if score >= 80
                                else "#f59e0b" if score >= 50
                                else "#ef4444"
                            )
                            st.markdown(
                                f"**ATS Match Score:** "
                                f"<span style='color:{score_color};font-size:1.4rem;font-weight:700'>"
                                f"{score}%</span>",
                                unsafe_allow_html=True,
                            )
                            if matched:
                                st.success(f"✅ Matched Skills: {', '.join(matched[:10])}")
                            if missing:
                                st.warning(f"⚠️ Missing Skills: {', '.join(missing[:10])}")
                            for rec in recs:
                                st.info(rec)
                        else:
                            st.warning("Please paste both your resume and the job description.")
