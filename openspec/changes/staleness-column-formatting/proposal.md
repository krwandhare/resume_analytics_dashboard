# Proposal: Data Staleness Column Formatting

## Summary
Add a component feature rule for formatting the "staleness" / age of application data across dashboard tables (`st.dataframe` and `st.data_editor`).

## Intent & Rationale
- **Backend Transformation**: Convert raw timestamp, datetime, or seconds values into clean, human-readable strings (e.g. "Just now", "15m ago", "Stale: 2 days old").
- **UI Pro Design Tokens**: Use accent color badges (🟢 Green for fresh data, 🟡 Yellow for moderate age, 🔴 Red for stale data) to provide instant visual signal.
- **Column Header & Tooltip**: Configure `st.column_config.TextColumn` with the public header label `"Data Age"` and an explanatory hover tooltip card.

## Proposed Changes
1. **Backend Transformer**: Add `format_staleness(raw_val)` utility function in `src/myproject/data_loader.py`.
2. **Dashboard UI Integration**: Update `overview.py` tables (`View Active / Pending`, `Recent Activity`, `View All Jobs`) to render the "Data Age" column using `st.column_config.TextColumn("Data Age", help="Elapsed time since this record was created or updated")`.
3. **Unit Tests**: Add unit tests for `format_staleness` in `tests/test_data_loader.py`.
