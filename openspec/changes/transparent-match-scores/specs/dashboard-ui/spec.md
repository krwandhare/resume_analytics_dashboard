## ADDED Requirements

### Requirement: Match Score Transparency Tooltip
The dashboard SHALL explicitly state that the Match Score is an indicator of ATS (Applicant Tracking System) pass likelihood, rather than a generic "semantic match."

#### Scenario: User checks the top-level Avg Match Score metric
- **WHEN** the user hovers over the help icon next to the "Avg Match Score" metric
- **THEN** they see a tooltip explaining that the score predicts the likelihood of passing an ATS screen

### Requirement: Actionable Match Score Categories
The dashboard SHALL categorize match scores into actionable buckets with clear labels to guide user behavior.

#### Scenario: User views match scores in data tables
- **WHEN** the user views a drill-down table containing match scores
- **THEN** the score is accompanied by an actionable label (e.g., >80% Strong Match / Ready to Apply, 60-79% Good Match / Needs Tailoring, <60% Low Match / Major Gaps)

### Requirement: Match Analysis Transparency
The dashboard SHALL expose the detailed AI reasoning behind a given match score for a specific job.

#### Scenario: User wants to know why they received a specific score
- **WHEN** the user views the details or insights for a specific job application
- **THEN** the system displays the `match_analysis` text detailing the exact strengths and gaps identified by the AI

### Requirement: Proactive Score Improvement Coaching
The dashboard SHALL extract actionable advice from the match analysis to teach users how to improve their resume for future applications.

#### Scenario: User receives a low match score
- **WHEN** the user views the details for a job with a low match score
- **THEN** the system provides an "Improve Your Score" tip block with actionable advice (e.g., "Add missing keyword X to your recent projects") based on the AI's analysis
