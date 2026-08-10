## Requirements

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
