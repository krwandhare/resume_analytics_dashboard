## Why

The previous implementation of the dashboard layout missed the mark on a few critical UI elements: the Plotly `KeyError` persists because the Pandas categorical schema forces unused categories to be plotted, the pipeline funnel lacks a graphical visual representation, the "Current Active Landscape" doesn't teach users how to interpret the data, and the KPI cards remain uncolored and plain.

## What Changes

- **True Categorical Fix**: Strip unused categories from the Match Score column using `.cat.remove_unused_categories()` before handing it to Plotly to permanently fix the `KeyError`.
- **Graphical Chevron Pipeline**: Replace the plain `st.columns` metrics with a beautifully styled, custom HTML/CSS chevron pipeline flow that visualizes the application funnel graphically without using the bulky Plotly funnel.
- **Active Landscape Tooltip/Expander**: Add an educational "💡 Insights" expander explicitly for the Current Active Landscape pie chart to teach users how to read their application health.
- **Meaningfully Colored KPIs**: Inject CSS styling via `st.markdown` to dynamically color the backgrounds of the top-level KPI metric cards (e.g., soft blue for applied, soft orange for interviewing) to tie into the semantic color palette.

## Capabilities

### New Capabilities
- `dashboard-ui/insights`: A new capability specifying that individual visual charts MUST include specific, contextual educational insights on how to interpret that specific slice of data (e.g., Active Landscape).

### Modified Capabilities
- `dashboard-ui`: Modifies the requirement for the horizontal pipeline and semantic color palette to explicitly mandate a *graphical* pipeline (like HTML chevrons) and *background-colored* KPI cards rather than just text emojis.

## Impact

- `src/myproject/analytics.py`: Complete overhaul of the pipeline visual rendering and categorical bug fix.
- `src/myproject/components/overview.py`: Injecting custom CSS to style the metric containers dynamically.
