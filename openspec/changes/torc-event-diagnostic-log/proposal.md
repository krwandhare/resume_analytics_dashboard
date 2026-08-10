# Proposal: Torc Event Diagnostic Logging

## Summary
Add diagnostic log tracing to the `job_application_events` processor in `data_loader.py` that outputs the raw `event_date` and calculated `staleness_days` for Torc application records.

## Rationale
To verify that data mapping and relative staleness calculations in backend data processing match the exact strings rendered on the Streamlit dashboard display during local test runs.

## Proposed Changes
1. **OpenSpec Specification**: Define diagnostic traceability requirement in `openspec/specs/event-pipeline/spec.md`.
2. **Data Loader Processor**: Inspect `events_df` in `load_historical_data` and log raw `event_date`, calculated `staleness_days`, and `format_staleness()` badges for Torc entries.
3. **Unit Tests**: Add unit tests in `tests/test_data_loader.py` to verify the diagnostic log trigger.
