## Why

Currently, the Resume Analytics Dashboard presents powerful insights and visualizations, but does not explain *how* to use them. A first-time user may be overwhelmed by the "Visual Analytics" and "Details & Insights" tabs, missing out on the core value: using data to identify bottlenecks and using AI coaching to improve applications. This change introduces a guided onboarding experience to bridge that gap.

## What Changes

- **Zero-Data Welcome Screen**: If a user has `0` jobs tracked, the application hides the complex analytics tabs and displays a focused welcome guide explaining the value proposition and providing a clear call to action to add their first job.
- **Contextual Help Expanders**: At the top of the "Visual Analytics" and "Details & Insights" tabs, add a visually distinct, collapsed-by-default expander titled "📖 How to read this data". This explains how to use the funnel to spot ATS/interview drop-offs, and how to use the AI match analysis.
- **Persistent Job Hunting Playbook**: Add a persistent help button or section in the sidebar that explains the philosophy of data-driven job hunting (e.g. what an ATS Match Score is and why tailoring matters).

## Capabilities

### New Capabilities

*(None)*

### Modified Capabilities

- `dashboard-ui`: Added requirements for zero-data onboarding state, contextual help expanders in analytics tabs, and a persistent sidebar guide.

## Impact

- `src/myproject/main.py`: Modified to render the zero-data state and sidebar guide.
- `src/myproject/components/analytics.py`: Modified to include the contextual help expander.
- `src/myproject/components/insights.py`: Modified to include the contextual help expander.
