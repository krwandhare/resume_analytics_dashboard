# Project: Resume Analytics Dashboard

## Context
- Goal: Analyze job application data to extract and visualize trends.
- The project is a Streamlit dashboard that fetches data from a Supabase 'jobs' table and generates insights using Plotly.
- Core logic resides in `src/myproject/`.

## Current Status
- Robust data engine and component architecture implemented.
- Automatic fallback demo dataset active when Supabase environment variables are missing or unconfigured.
- Weekly digest generation, dashboard preview/download, and Gmail API OAuth delivery are implemented and locally validated.
- Validation baseline: 62 tests passed; Python compilation, diff checks, and the no-email Streamlit smoke test passed.
- Feature commit `12199b8` is on `feature/claude-private-gmail-digest`; it has not been pushed and no pull request exists yet.

## Next Tasks
- [ ] Rotate the Supabase service-role credential exposed in earlier verbose test output; update the ignored local `.env` and revoke the old credential.
- [ ] Review HTTP/client logging so Supabase credentials and authorization headers cannot appear in test or runtime output.
- [ ] Push `feature/claude-private-gmail-digest` and open a pull request after confirming the remote target.
- [ ] Configure the ignored local Gmail sender/recipient values and authorize the send-only desktop OAuth client.
- [ ] Review the generated digest and perform one explicitly authorized live email delivery test.
- [ ] Install and verify the Monday macOS `launchd` schedule only after the live delivery test succeeds.

## Backlog
- [ ] Replace deprecated PyPDF2 usage with `pypdf`.
- [ ] Update Supabase client configuration to stop using deprecated `timeout` and `verify` parameters.

## Completed
- [x] Added an automated weekly analytics digest with week-over-week metrics, dashboard preview/download, Gmail API OAuth delivery, and a template for a private local Monday `launchd` schedule.
- [x] Expanded the pipeline status vocabulary, centralized canonical labels/colors, and excluded pre-application records from application conversion metrics.
- [x] Added the Discovered Jobs review queue with filtering, promotion, dismissal, and bounded cached Supabase loading.
- [x] Added interactive "➕ Add New Job Application" collapsible form directly in dashboard UI (`src/myproject/components/add_job_form.py`, `tests/test_add_job_form.py`).
- [x] Implemented automated email status ingestion & webhook alert handler (`src/myproject/email_ingestion.py`, `src/myproject/components/email_webhook_ingestion.py`, `tests/test_email_ingestion.py`).
- [x] Implemented PDF/DOCX resume upload & ATS skill match scorer (`src/myproject/resume_scorer.py`, `src/myproject/components/resume_scorer.py`).
- [x] Added CSV export capability for filtered job application data across sidebar and insights tabs (`src/myproject/components/sidebar.py`, `src/myproject/components/insights.py`).
- [x] Implement application status lifecycle pipeline visual chart.
- [x] Enhance error handling for missing/malformed Supabase data and environment variable validation (`src/myproject/data_loader.py`).
- [x] Refactor dashboard components into modular files (`src/myproject/components/`).
- [x] Create comprehensive pytest unit test suite (`tests/test_data_loader.py`, `tests/test_resume_scorer.py`, `tests/test_email_ingestion.py`).
- [x] Removed mistakenly created `src/myproject/resume_parser.py`.
- [x] Initialized `TODO.md` for project tracking.
- [x] Implemented interactive filtering by 'Company' and 'Status' in the dashboard.
- [x] Created comprehensive README.md documentation.
