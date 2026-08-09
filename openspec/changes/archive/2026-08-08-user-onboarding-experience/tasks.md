## 1. Zero-Data Onboarding State

- [x] 1.1 In `main.py`, identify where `filtered_data` is passed to the dashboard components.
- [x] 1.2 Add a condition: `if len(filtered_data) == 0:` to intercept the rendering.
- [x] 1.3 Inside this condition, render a `st.container()` that displays a "Welcome to Resume Analytics" message and explains the value proposition (Track, Analyze, Improve).
- [x] 1.4 Include a call-to-action button or clear instruction on how to add a job.
- [x] 1.5 Wrap the existing tabs (`Overview`, `Visual Analytics`, `Details & Insights`) in an `else:` block so they are hidden when there is no data.

## 2. Contextual Help Expanders

- [x] 2.1 In `src/myproject/components/analytics.py`, add `with st.expander("📖 How to read this data", expanded=False):` at the top of the analytics section.
- [x] 2.2 Add markdown inside this expander explaining how to identify bottlenecks in the funnel and timeline.
- [x] 2.3 In `src/myproject/components/insights.py`, add `with st.expander("📖 How to read this data", expanded=False):` at the top of the insights section.
- [x] 2.4 Add markdown inside this expander explaining how to use AI Match Scores and coaching tips to tailor resumes.

## 3. Persistent Sidebar Guide

- [x] 3.1 In `main.py`, locate the `with st.sidebar:` block.
- [x] 3.2 Add an `st.expander("📚 Job Hunting Playbook", expanded=False)` to the sidebar.
- [x] 3.3 Fill the expander with brief philosophical guidance on data-driven job hunting, ATS optimization, and what makes a good application.
