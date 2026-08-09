## Why

The current Match Score Distribution chart intermittently crashes (`KeyError`) because Plotly's histogram fails when a specified category has zero occurrences in the dataset. Additionally, the Application Funnel chart (`go.Funnel`) feels bulky and presents a grey, uninteresting visual flow, while the rest of the dashboard lacks a cohesive, vibrant color scheme that makes the data intuitive and premium.

## What Changes

- **Robust Plotly Fix**: Dynamically filter the `color_discrete_map` for the Match Score histogram so it only maps categories that actually exist in the dataframe, eliminating the `KeyError` entirely.
- **Horizontal Pipeline View**: Replace the bulky Plotly `go.Funnel` chart with a sleek, horizontal pipeline view using native Streamlit columns and colored metrics to show application progression.
- **Vibrant Semantic Styling**: Introduce a cohesive, modern color palette across all charts and UI components (e.g., using pill-like status badges or colored metrics) to make the dashboard feel premium and engaging.

## Capabilities

### New Capabilities
*(None)*

### Modified Capabilities
- `dashboard-ui`: Modifies the requirement for the visual funnel representation to mandate a horizontal pipeline flow instead of a bulky vertical funnel block, and specifies that a vibrant, semantic color scheme must be used across visual metrics.

## Impact

- `src/myproject/analytics.py`: Bug fix for `Match Quality` categorization, replacing `go.Funnel` with `st.columns` metrics, and applying new color schemes to charts.
- `src/myproject/components/overview.py`: Applying the vibrant semantic styling to top-level KPI metrics.
