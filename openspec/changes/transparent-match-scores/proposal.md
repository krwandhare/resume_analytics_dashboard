## Why

Currently, the "Avg Match Score" is a black box to users, with only a small tooltip stating it is an "AI-calculated semantic match." First-time users don't know how it is calculated, whether a given score is "good," or what actions they should take based on the score. Furthermore, users want to know how to proactively improve their score for upcoming jobs. By surfacing the AI's reasoning (which is already stored in the database as `match_analysis`) and providing actionable score labels and improvement tips, we can build trust and make the dashboard a proactive coaching tool rather than just a passive reporting tool.

## What Changes

- Update the "Avg Match Score" tooltip to clearly state that it predicts the likelihood of passing an ATS (Applicant Tracking System) screen.
- Categorize match scores into actionable buckets with clear labels (e.g., >80% Strong Match / Ready to Apply; 60-79% Good Match / Needs Tailoring; <60% Low Match / Major Gaps).
- Display these actionable labels in the job drill-down tables (e.g., "View All Jobs").
- Surface the `match_analysis` text from the database in the Job Details view to show exactly why a score was given.
- Add an "Improve Your Score" section or tip block in the Job Details or Insights tab that extracts actionable advice from the `match_analysis` (e.g., "Missing Python skills - add your recent project") to teach users how to tailor their resume for future applications.

## Capabilities

### New Capabilities
None

### Modified Capabilities
- `dashboard-ui`: Adding Match Score transparency, actionable categorization labels, and proactive score improvement tips.

## Impact

- `src/myproject/components/overview.py`: Updates to the Avg Match Score metric tooltip and data table displays.
- `src/myproject/components/insights.py` (or similar detailed views): Updates to display the `match_analysis` and actionable improvement tips when viewing specific job details.
- `src/myproject/analytics.py`: Potential updates to ensure the color-coding aligns with the new actionable labels.
