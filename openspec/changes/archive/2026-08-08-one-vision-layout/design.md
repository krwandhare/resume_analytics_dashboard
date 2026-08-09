## Context

See proposal.md - Why.

## Goals / Non-Goals

**Goals:**
- Eliminate tabs in `main.py` in favor of a top-down single-page dashboard.
- Display visual charts side-by-side using `st.columns` to maximize vertical space.
- Prevent `KeyError` crashes in `px.histogram` when Match Quality categories are missing.

**Non-Goals:**
- Removing or heavily modifying existing charting logic (other than fixing the Pandas categorical bug).

## Decisions

**1. One Vision Layout Construction:**
In `main.py`, instead of using `st.tabs()`, we will stack the components linearly:
1. `render_overview()` (KPIs at the top)
2. `generate_analytics()` (Visual charts in the middle)
3. `render_insights()` (Data tables at the bottom)

**2. Analytics Grid Packing:**
Inside `generate_analytics()` (in `analytics.py`), we will move the Funnel Chart and the Active Landscape (Pie Chart) into a 2-column grid to save vertical space. The Match Score Distribution will follow.

**3. Fixing the `KeyError`:**
In `analytics.py`, before calling `px.histogram`, we will ensure the `Match Quality` column is cast to a Categorical type:
```python
score_df['Match Quality'] = pd.Categorical(
    score_df['match_score'].apply(score_color),
    categories=['High Match (>80%)', 'Medium Match (50-80%)', 'Low Match (<50%)'],
    ordered=True
)
```
This forces Pandas and Plotly to acknowledge all 3 categories, even if the count is zero for one of them, which prevents the `KeyError` inside `plotly.express`.

## Risks / Trade-offs

- **Risk:** Stacking all components might make the page longer if there is a lot of data.
  **Mitigation:** By packing the charts side-by-side into columns, we minimize the vertical footprint. The data table at the bottom already has internal scrolling.
