## Purpose
Provides the layout, terminology, and visual hierarchy rules for the main dashboard interface to ensure a non-technical, intuitive user experience.

## Requirements

### Requirement: Non-technical Data Presentation
The dashboard SHALL present data without exposing underlying database table names (like `jobs` or `job_applications`) in the main UI text or sidebar filters.

#### Scenario: User reads the dashboard introduction
- **WHEN** the user views the top introduction text
- **THEN** they see a human-readable summary of the dashboard's purpose without bullet points explaining database schema

### Requirement: Subtle Success States
The dashboard SHALL display data loading success messages as subtle indicators rather than large, visually overpowering alert boxes.

#### Scenario: User loads the dashboard successfully
- **WHEN** the live job records are successfully fetched from the database
- **THEN** the record count is displayed as a subtle subtitle or sidebar element rather than a green success alert

### Requirement: Data Source Tooltips
The dashboard SHALL hide complex data source explanations and metric calculation logic behind hoverable tooltips.

#### Scenario: User wants to understand a KPI metric
- **WHEN** the user hovers over the help icon next to a KPI metric
- **THEN** a tooltip displays the calculation logic and data source for that specific metric

### Requirement: Visual Freshness Indicator
The dashboard SHALL display the time of the last data synchronization in the sidebar.

#### Scenario: User checks data freshness
- **WHEN** the user looks at the sidebar filters
- **THEN** they see a "Last synced: Today at [Time]" indicator

### Requirement: Tab Hierarchy
The dashboard SHALL eliminate tabbed navigation in favor of a single-pane grid hierarchy. KPIs MUST be displayed at the top, followed by visualization charts side-by-side, and followed by the detailed data tables at the bottom.

#### Scenario: User views the dashboard layout
- **WHEN** the user views the dashboard
- **THEN** the Overview, Visual Analytics, and Details & Insights sections are all visible simultaneously without requiring tab clicks
- **THEN** visual charts (like the Funnel and Status pie chart) are positioned side-by-side to minimize vertical scrolling

### Requirement: Table Row Numbering
The dashboard SHALL explicitly number the rows in all drill-down data tables to provide an easily verifiable total count.

#### Scenario: User checks the total jobs in a table
- **WHEN** the user views a drill-down table (e.g., View All Jobs, View Interviews)
- **THEN** the first column is a "Sr No" (Serial Number) column that increments from 1 to the total number of rows

### Requirement: Temporal Context in Tables
The dashboard SHALL display the date a job was added or applied to in the data tables, allowing users to understand the timeline and sort by recency.

#### Scenario: User wants to sort recent applications
- **WHEN** the user views the "View All Jobs" or "View Interviews" tables
- **THEN** an "Applied Date" column is visible, populated from the underlying tracking dates (`first_seen_at` or `applied_at`)

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

### Requirement: Human-Readable Data Age Formatting
The dashboard SHALL convert raw data staleness values (seconds, timestamps, or datetimes) into human-readable strings formatted with visual status tokens.

#### Scenario: Data is less than 1 hour old
- **WHEN** the record staleness is under 60 minutes
- **THEN** the system displays a green indicator with the relative time (e.g. `🟢 Just now` or `🟢 15m ago`)

#### Scenario: Data is 1 to 2 days old
- **WHEN** the record staleness is between 24 and 48 hours
- **THEN** the system displays a yellow status token with day age (e.g. `🟡 1d old`)

#### Scenario: Data is more than 2 days old
- **WHEN** the record staleness exceeds 48 hours
- **THEN** the system displays a muted red status token indicating staleness (e.g. `🔴 Stale: 3d old`)

### Requirement: Standardized Data Age Column Configuration
The dashboard data tables SHALL render the staleness column with the public header label `"Data Age"` and an explanatory tooltip hover card.

#### Scenario: User inspects table header for data age
- **WHEN** the user views a dashboard data table containing the staleness metric
- **THEN** the column header is labeled `"Data Age"`
- **THEN** hovering over the header displays a tooltip card explaining the calculation logic

