# Event Pipeline Specs

## Purpose
Defines data extraction, merging, and diagnostic verification rules for `job_application_events` and historical application tracking.

## Requirements

### Requirement: Diagnostic Pipeline Traceability for Event Staleness
The `job_application_events` data processor SHALL log diagnostic details (raw `event_date`, calculated `staleness_days`, and formatted `Data Age` string) for application events across all companies and timestamp ranges (fresh, moderate, stale, future, and null).

#### Scenario: Application events are loaded from database
- **WHEN** historical application events are merged with application records
- **THEN** the system logs a diagnostic entry containing:
  - Application ID
  - Company name
  - Raw `event_date` value
  - Calculated `staleness_days` float
  - Formatted `Data Age` token string
- **THEN** the diagnostic log allows local test runs to verify accuracy against dashboard display metrics across diverse timestamp ranges
