# Proposal: Expand Interview Statuses

## What
Expand the application status lifecycle to provide higher-resolution feedback on why processes stop, specifically distinguishing between company-driven rejections and user-driven rejections, and separating early recruiter screens from later interviews.

## Why
Currently, a generic "Rejected" or "Pending" status makes it hard to extract actionable metrics. By adding distinct statuses like `Irejected`, `Cancelled`, `Not H1B Friendly`, and `Recruiter Call`, the user can visualize exact drop-off points and differentiate between system issues (visa) and personal choice (consultancy, withdrew).

Additionally, this change expands the dashboard into a full end-to-end pipeline tracker by introducing pre-application statuses. `Saved for later` allows tracking jobs on a wishlist, while `Not Applied` tracks jobs reviewed but explicitly rejected by the user before applying.

## Non-Goals
- Changing the underlying database table structure for jobs (we are just updating the allowed string values and categorization in the Python code).
