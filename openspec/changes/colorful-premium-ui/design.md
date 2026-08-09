## Context

See proposal.md - Why.

## Goals / Non-Goals

**Goals:**
- Fix the `KeyError` by filtering the Plotly category colors dynamically.
- Replace the vertical `go.Funnel` chart with a horizontal Streamlit metrics pipeline.
- Implement vibrant, semantic colors across the dashboard (Overview metrics, Match Score charts).

**Non-Goals:**
- Changing underlying data loading logic.
- Rewriting the Details & Insights table (aside from colorizing if possible).

## Decisions

**1. Dynamic Color Mapping (`analytics.py`):**
To completely solve the Plotly crash on empty categories, we will filter `color_discrete_map`:
```python
color_map = {
    'High Match (>80%)': '#10B981',
    'Medium Match (50-80%)': '#F59E0B',
    'Low Match (<50%)': '#EF4444'
}
existing_categories = score_df['Match Quality'].unique()
filtered_map = {k: v for k, v in color_map.items() if k in existing_categories}
# Pass filtered_map to color_discrete_map
```

**2. Horizontal Pipeline Layout (`analytics.py`):**
Instead of using `go.Funnel`, we will map the four stages (Applied, Interviewing, Offer Received, Hired) into four columns:
```python
col1, col2, col3, col4 = st.columns(4)
col1.metric("Applied", total_apps)
col2.metric("Interviewing", total_interviews)
col3.metric("Offers", total_offers)
col4.metric("Hired", total_hired)
```
*Note: To make it look like a pipeline, we can use markdown styling with colored emojis or inline HTML for arrows if needed, but standard `st.metric` in a 4-column layout provides the desired sleek, grey-free look natively.*

**3. Vibrant KPIs (`overview.py` & `analytics.py`):**
In `overview.py`, the top-level KPIs will be enhanced. If possible using `st.markdown`, we can style the metric numbers with the semantic colors (Emerald, Amber, Rose, Blue) to give it a premium "dashboard" feel. 

## Risks / Trade-offs

- **Risk:** Dropping the visual funnel might remove the immediate "shape" of drop-offs.
  **Mitigation:** The horizontal columns still convey the same numbers cleanly, and `st.metric` naturally supports delta values if we choose to show drop-off percentages in the future.
