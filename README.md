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

## Weekly email delivery

The `Weekly analytics digest` GitHub Actions workflow runs every Monday at 13:00 UTC and can also be triggered manually. Configure these repository secrets before enabling it:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SMTP_HOST`, `SMTP_USERNAME`, and `SMTP_PASSWORD`
- `WEEKLY_DIGEST_FROM` and `WEEKLY_DIGEST_TO`
- `SMTP_PORT` (optional; defaults to `587`)

Set the repository variable `SMTP_STARTTLS` to `false` only when the mail server explicitly requires an unencrypted SMTP connection. The same delivery can be tested locally without committing credentials:

```bash
python scripts/send_weekly_digest.py
```

## Project Structure

- `src/myproject/main.py`: Main Streamlit application entry point.
- `src/myproject/analytics.py`: Visualization logic using Plotly.
- `inspect_db.py`: Utility script for database inspection.
