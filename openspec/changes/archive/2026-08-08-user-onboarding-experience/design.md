## Context

See proposal.md - Why.

## Goals / Non-Goals

**Goals:**
- Provide a clean, guided onboarding flow for users with 0 jobs tracked.
- Embed contextual "how-to" guides within the complex analytics tabs.
- Create a persistent Job Hunting Playbook in the sidebar.

**Non-Goals:**
- Interactive step-by-step tours (e.g. intro.js).
- Storing "has_seen_onboarding" state in the database (we will simply rely on `total_tracked == 0` for simplicity).

## Decisions

**1. Zero-Data State Implementation:**
We will use Streamlit's conditional rendering in `main.py` (or within the `render_overview` layer) to check if `len(df) == 0`. If so, we bypass rendering the tabs and instead use `st.container()` to render a welcome message and a clear button to "Add First Job" (which can just trigger the existing add job flow).

**2. Contextual Help Expanders:**
In `analytics.py` and `insights.py`, we will prepend an `st.expander("📖 How to read this data", expanded=False)`. This is native to Streamlit and requires no extra CSS or JS.

**3. Persistent Sidebar Guide:**
In `main.py`, inside the `with st.sidebar:` block, we will add an `st.expander("📚 Job Hunting Playbook", expanded=False)` containing a markdown guide on ATS match scores, funnel bottlenecks, and resume tailoring. Alternatively, we can use `st.dialog` if available, but an expander is simpler and backwards-compatible. We'll stick to a sidebar expander.

## Risks / Trade-offs

- **Risk:** Users with 0 jobs might want to see what the dashboard looks like before adding data.
  **Mitigation:** The welcome screen can include a placeholder screenshot or explicitly state "Add a job to unlock the dashboard." (Alternatively, we could offer "Load Demo Data", but that is out of scope).
