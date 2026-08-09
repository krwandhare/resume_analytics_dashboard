## 1. Dynamic Color Mapping (Match Score Histogram)

- [x] 1.1 In `analytics.py`, locate the `Match Score Distribution` chart generation.
- [x] 1.2 Define a `color_map` dictionary for Match Quality and extract `existing_categories` using `score_df['Match Quality'].unique()`.
- [x] 1.3 Create a `filtered_map` mapping only existing categories, and pass it to `color_discrete_map` in `px.histogram`.

## 2. Horizontal Pipeline Layout (Funnel Replacement)

- [x] 2.1 In `analytics.py`, locate the `Build Funnel Data` section and remove the `go.Funnel` figure creation.
- [x] 2.2 Extract the counts for 'Applied', 'Interviewing', 'Offer Received', and 'Hired' from `funnel_df`.
- [x] 2.3 Render a `st.columns(4)` block and use `st.metric` (or colored markdown blocks) to display these 4 stages horizontally.

## 3. Vibrant KPIs & UI Polish

- [x] 3.1 In `overview.py`, apply semantic styling (e.g., emojis or markdown colors) to top-level KPIs.
- [x] 3.2 Review other visual elements in `analytics.py` (like the pie chart) to ensure they use a cohesive, premium color palette instead of defaults or greys.
