## ADDED Requirements

### Requirement: Horizontal Pipeline Representation
The dashboard SHALL visualize the application funnel progression using a sleek, horizontal pipeline layout rather than a bulky vertical funnel block, optimizing space and improving modern aesthetic appeal.

#### Scenario: User views their application pipeline
- **WHEN** the user views the Visual Analytics section
- **THEN** they see a horizontal flow of metrics (e.g., Applied -> Interviewing -> Hired)
- **THEN** the pipeline utilizes colored, inline deltas or styled containers rather than a large grey connected funnel

### Requirement: Semantic Color Palette
The dashboard SHALL employ a cohesive, vibrant semantic color palette across all graphical visualizations (pie charts, histograms) and key UI components to ensure data is intuitively understandable.

#### Scenario: User analyzes Match Score quality
- **WHEN** the user views the Match Score Distribution chart
- **THEN** the chart uses semantic colors indicating quality (e.g., green for High Match, amber for Medium Match, red for Low Match)
- **THEN** missing data categories do not cause application crashes
