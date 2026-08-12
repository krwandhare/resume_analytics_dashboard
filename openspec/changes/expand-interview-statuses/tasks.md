# Tasks: Expand Interview Statuses

- [x] **Task 1: Update Constants and Forms**
  - Update `STATUS_COLORS` in `src/myproject/analytics.py` with all 14 new statuses and distinct color codes.
  - Update `status` selectboxes in `src/myproject/components/add_job_form.py` and `src/myproject/components/insights.py`.

- [x] **Task 2: Update Metric Logic**
  - Update `pending_count`, `total_interviews`, and `total_offers` in `src/myproject/components/overview.py` to correctly map the new active pipeline statuses (like `Recruiter Call`).

- [x] **Task 3: Test and Verify**
  - Restart the streamlit server.
  - Add a test job with the new `Irejected` status and verify it appears in the Insights filter and Analytics charts without crashing.

- [x] **Task 4: Add Pre-Application Statuses**
  - Add `Saved for later` and `Not Applied` to `STATUS_COLORS` in `analytics.py`.
  - Add them to the status dropdowns in `add_job_form.py`, `insights.py`, and `overview.py` data editor columns.
  - Exclude them from the "Total Applications" metric logic in `overview.py` (ensure they aren't counted as active/applied).
  - Provide a new SQL snippet to the user to update the `job_applications_status_check` database constraint to allow these two new strings.
