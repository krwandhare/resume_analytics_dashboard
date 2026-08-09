## ADDED Requirements

### Requirement: Table Row Numbering
The dashboard SHALL explicitly number the rows in all drill-down data tables to provide an easily verifiable total count.

#### Scenario: User checks the total jobs in a table
- **WHEN** the user views a drill-down table (e.g., View All Jobs, View Interviews)
- **THEN** the first column is a "Sr No" (Serial Number) column that increments from 1 to the total number of rows

### Requirement: Temporal Context in Tables
The dashboard SHALL display the date a job was added or applied to in the data tables, allowing users to understand the timeline and sort by recency.

#### Scenario: User wants to sort recent applications
- **WHEN** the user views the "View All Jobs" or "View Interviews" tables
- **THEN** an "Applied Date" column is visible, populated from the underlying tracking dates (`first_seen_at` or `applied_at`)
