## 1. Extract Dates

- [x] 1.1 In `overview.py`, update the "View All Jobs" data logic to extract `first_seen_at` for live jobs and `applied_at` for historical applications.
- [x] 1.2 Format the extracted dates as `YYYY-MM-DD` (or leave blank if missing) and assign them to an `Applied Date` key in the dictionary.
- [x] 1.3 Ensure the `Applied Date` column is added to the list of displayed columns for "View All Jobs".

## 2. Inject Serial Numbers

- [x] 2.1 For the "View All Jobs" drilldown, inject a `Sr No` column dynamically using `display_df.insert(0, 'Sr No', range(1, len(display_df) + 1))` just before rendering the table.
- [x] 2.2 For the "View Unique Companies" drilldown, inject the `Sr No` column dynamically before rendering.
- [x] 2.3 For the "View Active / Pending" drilldown, inject the `Sr No` column dynamically before rendering.
- [x] 2.4 For the "View Interviews" drilldown, inject the `Sr No` column dynamically before rendering.
