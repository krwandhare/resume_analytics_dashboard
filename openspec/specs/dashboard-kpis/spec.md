## Purpose
Defines the calculation logic and data sources for the high-level dashboard Key Performance Indicators (KPIs) to ensure accuracy and consistency across views.

## Requirements

### Requirement: Total Jobs Tracked KPI Calculation
The "Total Jobs Tracked" KPI SHALL display the sum of all live jobs currently tracked and any manual/historical applications that do not overlap with live jobs.

#### Scenario: User views the overview dashboard
- **WHEN** the dashboard loads the high-level metrics
- **THEN** the "Total Jobs Tracked" metric shows the true total count of all unique job applications across both data streams (live and historical)
