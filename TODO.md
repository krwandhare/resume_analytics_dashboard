# Project: Resume Analytics Dashboard

## Context
- Goal: Analyze job application data to extract and visualize trends.
- The project is a Streamlit dashboard that fetches data from a Supabase 'jobs' table and generates insights using Plotly.
- Core logic resides in `src/myproject/`.

## Current Status
- Robust data engine & component architecture implemented.
- Automatic fallback demo dataset active when Supabase environment variables are missing/unconfigured.

## Next Tasks
- [ ] Add CSV export for filtered application data.
- [x] Implement application status lifecycle pipeline visual chart.

## Backlog
- [ ] Add PDF resume file upload & skill match scorer integration.

## Completed
- [x] Enhance error handling for missing/malformed Supabase data and environment variable validation (`src/myproject/data_loader.py`).
- [x] Refactor dashboard components into modular files (`src/myproject/components/`).
- [x] Create comprehensive pytest unit test suite (`tests/test_data_loader.py`).
- [x] Removed mistakenly created `src/myproject/resume_parser.py`.
- [x] Initialized `TODO.md` for project tracking.
- [x] Implemented interactive filtering by 'Company' and 'Status' in the dashboard.
- [x] Created comprehensive README.md documentation.
