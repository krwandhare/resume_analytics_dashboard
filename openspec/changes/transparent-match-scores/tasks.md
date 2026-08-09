## 1. UI Label Categories

- [x] 1.1 In `overview.py`, define a helper function to convert numeric `match_score` into a categorical label with an emoji (e.g., 🟢 Strong Match (Ready), 🟡 Good Match (Tailor Resume), 🔴 Low Match (Major Gaps)).
- [x] 1.2 Update the `display_rows` logic in the "View All Jobs" section to apply this label to the `match_score` value.
- [x] 1.3 Ensure the table columns dynamically render the new labeled strings correctly.

## 2. Match Score Tooltips

- [x] 2.1 In `overview.py`, update the `st.metric` tooltip for "Avg Match Score" to clearly state: "Predicts your chance of passing an ATS screen. >80% is ready to apply."

## 3. Surface AI Analysis & Coaching Tips

- [x] 3.1 In `insights.py` (or the Job Details logic), ensure the `match_analysis` text is pulled from the job record.
- [x] 3.2 Add an `st.info` or `st.expander` block in the Job Details view titled "💡 How to Improve Your Score for Upcoming Jobs".
- [x] 3.3 Render the `match_analysis` text inside this block to show the user exactly why they received their score.
- [x] 3.4 If `match_analysis` is empty, fallback to a generic coaching tip (e.g., "Tailor your resume by adding keywords from the job description").
