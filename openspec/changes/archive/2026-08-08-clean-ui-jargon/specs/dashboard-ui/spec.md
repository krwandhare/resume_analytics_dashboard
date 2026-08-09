## Purpose
Provides the layout, terminology, and visual hierarchy rules for the main dashboard interface to ensure a non-technical, intuitive user experience.

## ADDED Requirements

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
The dashboard SHALL visually separate the main content tabs from the top-level overview metrics using padding or a divider line.

#### Scenario: User scrolls to the interactive tabs
- **WHEN** the user views the tabs (Overview, Visual Analytics, Details)
- **THEN** there is a clear visual divider separating the tabs from the KPI metrics above them
