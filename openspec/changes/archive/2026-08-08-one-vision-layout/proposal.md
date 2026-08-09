## Why

The current dashboard hides valuable information behind three tabs (Overview, Visual Analytics, Details & Insights), forcing users to click around and lose context. Additionally, there is a known crash (`KeyError: 'Low Match (<50%)'`) when generating the Match Score histogram if certain categorical data is missing. This change optimizes the layout into a "single-pane-of-glass" view to minimize scrolling and fixes the underlying categorical data bug.

## What Changes

- **Layout Overhaul**: Replace the tabbed navigation with a grid-based layout using `st.columns`.
- **Top-Down Flow**: Display KPIs at the top, Visualizations (Funnel & Pie Chart) in the middle, and the Drill-down Data Table at the bottom.
- **Bug Fix**: Explicitly cast the `Match Quality` column to a Pandas Categorical type with a fixed set of categories before passing it to Plotly, preventing `KeyError` crashes.

## Capabilities

### New Capabilities
*(None)*

### Modified Capabilities
- `dashboard-ui`: Modifies the requirement for "Tab Hierarchy" to a "Single-Pane Grid Hierarchy" to eliminate tabs and reduce scrolling.

## Impact

- `src/myproject/main.py`: Layout changes to remove tabs and use `st.columns`.
- `src/myproject/analytics.py`: Bug fix for `Match Quality` categorization and layout adjustments to fit the new grid.
- `src/myproject/components/insights.py`: Layout adjustments to fit the new grid.
