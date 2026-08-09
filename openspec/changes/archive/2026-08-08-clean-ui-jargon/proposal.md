## Why

The current Job Intelligence Dashboard exposes too much technical database terminology (e.g., table names like `jobs`, `job_application_events`) to the user. This creates cognitive overload for first-time, non-technical users who simply want to track their job search progress. We need to streamline the UI to be more intuitive, less cluttered, and focused on business value rather than system plumbing.

## What Changes

- **Remove Database Jargon (Intro)**: Replace the technical bulleted list explaining database tables with a single, clear, human-readable introductory sentence.
- **Demote Success Alert**: Remove the massive green alert box for successful data loading. Move the record count to a subtle subtitle or sidebar element.
- **Hide Data Source Explanations**: Move the lengthy text explaining how KPIs are calculated into `help="..."` tooltips on the `st.metric` components.
- **Clean Sidebar Text**: Rewrite the filter instructions in the sidebar to be user-friendly, removing references to the `jobs` table.
- **Add Freshness Indicator**: Add a "Last synced: Today at [Time]" timestamp in the sidebar to build trust in data freshness.
- **Emphasize Tabs**: Add visual padding or a divider above the main section tabs to separate them from the overview section.

## Capabilities

### New Capabilities
- `dashboard-ui`: Defines the visual layout, tooltip requirements, and non-technical language constraints for the main dashboard interface.

### Modified Capabilities
*(None - no existing specs to modify)*

## Impact

- **UI Components**: `src/myproject/components/overview.py` and `src/myproject/main.py` will be updated to modify Streamlit layout and text.
- **Dependencies**: No new dependencies required.
- **Data Model**: No changes to the underlying database or data model.
