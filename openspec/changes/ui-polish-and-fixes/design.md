## Context

See proposal.md for motivation - the previous implementation of the colorful UI missed the mark by retaining the Pandas category KeyError and failing to visually render a graphical pipeline. 

## Goals / Non-Goals

**Goals:**
- Permanently fix the Plotly KeyError for unobserved categorical values.
- Replace the current text-based funnel metrics with a visually striking, CSS-based Chevron pipeline graph.
- Implement background colors for the KPI metric cards to make them pop.
- Provide educational insights for the Active Landscape.

**Non-Goals:**
- Completely rewriting the overall grid layout (sticking to the one-vision dashboard layout).
- Adding new data sources or charts.

## Decisions

### 1. Fixing the Plotly KeyError
**Decision**: Use `score_df['Match Quality'].cat.remove_unused_categories()` immediately before passing the dataframe to Plotly.
**Rationale**: Plotly inherently reads the schema of Pandas categorical columns and tries to force all declared categories onto the chart. Stripping unused categories directly from the Pandas Series stops Plotly from attempting to group by non-existent values, inherently fixing the `KeyError: 'Low Match (<50%)'`.

### 2. Custom HTML/CSS Chevron Pipeline
**Decision**: We will replace the 4 `st.columns` text metrics with a single `st.markdown(..., unsafe_allow_html=True)` rendering a CSS Flexbox row of chevrons.
**Rationale**: Native Streamlit elements cannot draw connected flow diagrams easily without using heavy libraries like `go.Sankey` or `go.Funnel` (which we rejected for being ugly). A custom HTML/CSS block allows us to use `clip-path: polygon(...)` to create sleek, connected chevron arrows that map perfectly to our `STATUS_COLORS` semantic palette.

### 3. KPI Metric Card Coloring
**Decision**: We will render the 5 top-level KPI cards as a custom HTML/CSS flexbox grid instead of using `st.metric`.
**Rationale**: Streamlit's native `st.metric` cannot have its background colored reliably without brittle DOM-hacking (like CSS `nth-child` selectors that break on Streamlit updates). By rendering the 5 metric cards inside a single `st.markdown` block, we gain total control over the background colors, padding, and layout, allowing us to perfectly match the semantic colors (e.g., green for interviews, blue for applied).

### 4. Educational Insights Expander
**Decision**: We will add an `st.expander("💡 Insights: What does this mean?")` directly below the "Current Active Landscape" pie chart in `analytics.py`.
**Rationale**: Contextual help belongs exactly where the user is looking. An expander keeps the UI clean while offering crucial interpretation advice (e.g., "Too much Blue? You're not getting callbacks. Lots of Orange? You're doing great!").

## Risks / Trade-offs

- **Risk**: Injecting custom HTML/CSS via `unsafe_allow_html=True` can sometimes clash with Streamlit's dark/light mode themes.
- **Mitigation**: We will use CSS variables or ensure our hardcoded semantic colors have enough contrast in both dark and light modes, and we will avoid setting hardcoded text colors where Streamlit's defaults would work better.
