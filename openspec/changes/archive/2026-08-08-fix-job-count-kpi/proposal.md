## Why

Currently, the "Total Jobs Tracked" KPI on the overview dashboard only counts the live jobs from the `jobs` table and ignores any jobs that exist solely in the historical `job_applications` table (e.g. manual batches). This leads to a mismatch between the top-level KPI (e.g. 23 jobs) and the drill-down view (which accurately merges both sources). We need the KPI to reflect the true total of all jobs being tracked.

## What Changes

- Modify the calculation for the "Total Jobs Tracked" metric in `overview.py` to add the count of historical/manual applications that do not overlap with live jobs.
- Update the metric's tooltip to explain that it includes both live and historical applications.

## Capabilities

### New Capabilities
- `dashboard-kpis`: Defines the business logic and data sources for the high-level dashboard metrics to ensure consistency.

### Modified Capabilities
*(None)*

## Impact

- **UI Components**: `src/myproject/components/overview.py` will have a revised calculation for `st.metric("Total Jobs Tracked", ...)`
- **Data Model**: No changes.
