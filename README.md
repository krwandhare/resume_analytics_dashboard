# Resume Analytics Dashboard

A Streamlit-based dashboard for visualizing and analyzing job application data stored in Supabase.

## Features

- **Dashboard:** Interactive visualization of job application metrics.
- **Filtering:** Filter data by Company and Application Status.
- **Analytics:** Visualizations for match score distribution, top companies, and application status breakdown.
- **Weekly digest:** Week-over-week pipeline metrics with Markdown download and optional scheduled email delivery.

## Prerequisites

- Python 3.9+
- A Supabase account and a project with a `jobs` table containing at least the following columns:
  - `company` (text)
  - `status` (text)
  - `match_score` (numeric, optional)
  - `job_title` (text, optional)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd resume_analytics_dashboard
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set environment variables:**
    Create a `.env` file or export the following variables in your terminal:
    ```bash
    export SUPABASE_URL="your-supabase-url"
    export SUPABASE_ANON_KEY="your-supabase-anon-key"
    ```

4.  **Run the dashboard:**
    ```bash
    streamlit run src/myproject/main.py
    ```

## Private weekly email delivery

Weekly email delivery runs locally through macOS `launchd`. Supabase, SMTP, and recipient credentials remain in the ignored local `.env` file and are never uploaded to GitHub variables or Actions secrets.

Test delivery locally with:

```bash
.venv/bin/python scripts/send_weekly_digest.py
```

See [Private weekly digest automation](docs/weekly-digest.md) for credential requirements, scheduler installation, verification, logs, and removal.

## Project Structure

- `src/myproject/main.py`: Main Streamlit application entry point.
- `src/myproject/analytics.py`: Visualization logic using Plotly.
- `src/myproject/weekly_digest.py`: Weekly summary generation and SMTP delivery.
- `scripts/send_weekly_digest.py`: Local scheduled-delivery entry point.
- `inspect_db.py`: Utility script for database inspection.
