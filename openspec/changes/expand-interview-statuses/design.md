# Design: Status Expansion

## Status Map & Color Coding
In `src/myproject/analytics.py` `STATUS_COLORS` mapping, we will add new hex values for a total of 16 statuses.
- **Pre-Application**: Light neutral or purple (`Saved for later`)
- **Active**: Blue/Teal (e.g., `Recruiter Call` can be a light blue)
- **Success**: Green (`Hired`)
- **Company Stopped**: Reds/Grays (`Cancelled`, `Not H1B Friendly`, `Ghosted`)
- **User Stopped**: Oranges/Yellows (`Irejected`, `Withdrew`, `Consultancy`, `Not Applied`)

## Component Updates
- **`add_job_form.py` & `insights.py`**: Update status dropdowns to include all 16 statuses.
- **`overview.py` & Metrics**:
  - `pending_count`, `total_interviews`, `live_interviews` correctly include `recruiter call`.
  - Ensure `Saved for later` and `Not Applied` DO NOT increment the "Total Applications" metric, as no application was sent. They should only count towards total tracked jobs.
