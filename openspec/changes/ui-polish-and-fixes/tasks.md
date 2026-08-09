## 1. Fix Plotly KeyError

- [x] 1.1 In `src/myproject/analytics.py`, locate the Match Score Distribution logic.
- [x] 1.2 Apply `.cat.remove_unused_categories()` to `score_df['Match Quality']` before passing it to `px.histogram`.

## 2. Graphical Chevron Pipeline

- [x] 2.1 In `src/myproject/analytics.py`, locate the `Horizontal Pipeline` section.
- [x] 2.2 Replace the `st.columns` and `st.metric` logic with an HTML string styled using CSS to display interconnected chevrons mapping to the 4 stages (Applied, Interviewing, Offers, Hired) and their counts.
- [x] 2.3 Render the HTML string using `st.markdown(..., unsafe_allow_html=True)`.

## 3. Colored KPI Cards

- [x] 3.1 In `src/myproject/components/overview.py`, locate the top 5 `st.metric` definitions.
- [x] 3.2 Construct an HTML flexbox grid containing custom styled cards for each metric, applying semantic background colors matching the visual palette (e.g., green for Hired, blue for Applied).
- [x] 3.3 Render the grid using `st.markdown(..., unsafe_allow_html=True)` instead of standard Streamlit metrics.

## 4. Educational Insights

- [x] 4.1 In `src/myproject/analytics.py`, locate the "Current Active Landscape" section.
- [x] 4.2 Below the pie chart, insert an `st.expander("💡 Insights: What does this mean?")`.
- [x] 4.3 Add markdown text inside the expander explaining how to interpret the distribution of Active Landscape statuses.
