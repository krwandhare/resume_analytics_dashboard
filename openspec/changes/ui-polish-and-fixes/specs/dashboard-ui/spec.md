## ADDED Requirements

### Requirement: Graphical Pipeline Visualization
The dashboard SHALL visualize the application funnel using a graphical pipeline representation (such as connected CSS chevrons or flow diagrams) rather than plain text metrics.

#### Scenario: User views the application funnel
- **WHEN** the user views the application funnel progression
- **THEN** the stages are displayed as a connected, graphical pipeline indicating flow.

### Requirement: Colored KPI Cards
The dashboard SHALL dynamically apply semantic background colors to the top-level KPI metric cards to visually reinforce the meaning of each metric.

#### Scenario: User views the top-level KPIs
- **WHEN** the user views the Overview metrics (e.g., Active/Pending, Interviews)
- **THEN** the background of the metric cards is styled with a corresponding semantic color instead of remaining plain or gray.
