## Why

Currently, the drill-down tables in the dashboard do not display a serial number, making it difficult for users to cross-check the number of rows against the top-level KPIs. Additionally, essential temporal context (the date the job was posted or applied to) is hidden in several views, making it harder to track and sort recent applications.

## What Changes

- Add a `Sr No` (Serial Number) column to all drill-down tables (View All Jobs, View Unique Companies, View Active/Pending, View Interviews) as the first column.
- Map the `first_seen_at` (from live tracker) and `applied_at` (from manual jobs) into a unified `Applied Date` column.
- Display the `Applied Date` column in the "View All Jobs" and "View Interviews" tables for better context.

## Capabilities

### New Capabilities
*(None)*

### Modified Capabilities
- `dashboard-ui`: Modifies the data presentation requirements for dashboard tables to include explicit row numbering and temporal context (Applied Date).

## Impact

- **UI Components**: `src/myproject/components/overview.py` will have updated table generation logic to include the new columns before rendering.
- **Data Model**: No underlying database changes; this is purely a frontend mapping change.
