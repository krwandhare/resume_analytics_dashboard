# Core Status Lifecycle Delta

## Status Enumeration
The application status must support the following distinct phases in all dropdowns and filters:
- **Active Pipeline**: `Applied`, `Reviewing`, `Recruiter Call`, `Interviewing`, `Offer Received`
- **Success Terminal**: `Hired`
- **Company Stopped Terminal**: `Rejected`, `Cancelled`, `Not H1B Friendly`, `Ghosted`
- **User Stopped Terminal**: `Irejected`, `Withdrew`, `Consultancy`

## Visualization & Metrics
- Charts and metrics must accurately group these new statuses.
- "Total Interviews" should encompass `Recruiter Call` and `Interviewing`.
- Colors should clearly distinguish terminal states based on origin (User vs. Company).
