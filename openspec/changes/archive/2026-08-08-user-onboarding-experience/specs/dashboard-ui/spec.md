## ADDED Requirements

### Requirement: Zero-Data Onboarding State
The system SHALL display a full-page onboarding guide instead of the standard analytics tabs when the user has exactly 0 jobs tracked. The guide SHALL explain the core value proposition and provide a clear call to action to add a job.

#### Scenario: User with 0 jobs views dashboard
- **WHEN** the dashboard loads for a user with `total_tracked` == 0
- **THEN** the system hides the "Overview", "Visual Analytics", and "Details & Insights" sections
- **THEN** the system displays a "Welcome" guide with instructions and a call to action

### Requirement: Contextual Help Expanders
The system SHALL display a collapsed-by-default contextual help expander at the top of the "Visual Analytics" and "Details & Insights" tabs (when visible). The expander SHALL explain how to read the data in that specific tab.

#### Scenario: User views Visual Analytics tab
- **WHEN** the user navigates to the "Visual Analytics" tab and has > 0 jobs
- **THEN** a collapsed expander titled "📖 How to read this data" is visible at the top
- **THEN** expanding it shows guidance on identifying funnel bottlenecks

#### Scenario: User views Details & Insights tab
- **WHEN** the user navigates to the "Details & Insights" tab and has > 0 jobs
- **THEN** a collapsed expander titled "📖 How to read this data" is visible at the top
- **THEN** expanding it shows guidance on using AI Match Scores to tailor resumes

### Requirement: Persistent Sidebar Guide
The system SHALL provide a persistent "Job Hunting Playbook" guide accessible from the main navigation sidebar.

#### Scenario: User clicks sidebar guide
- **WHEN** the user interacts with the "Job Hunting Playbook" button in the sidebar
- **THEN** the system displays philosophical guidance on data-driven job hunting (e.g., via a modal dialog or expanded sidebar section)
