# Data Visualization Rule (Learned)

- **Categorical Data Casing:** When visualizing categorical data (like statuses, tags, or states) from databases in pandas/Plotly, ALWAYS normalize the string casing (e.g., using `.str.title()` or `.str.lower()`) before grouping, filtering, or mapping against hardcoded literal lists. Do not assume the database enforces a specific casing for text fields.

- **Context-Rich Activity Feeds:** When building activity timelines or event feeds in a UI, NEVER display raw, unlinked event records. ALWAYS join/enrich the event data with its parent relational context (e.g., Company, Role, User Name). Furthermore, feeds must be **highly scannable** (using color-coded status badges/emojis), **filterable** (providing UI toggles to filter out noise, defaulting to high-signal views), **compact** (collapsing/deduplicating multiple updates for the same entity into a single row to prevent vertical sprawl), and **time-aware** (surfacing "Days Since Last Update" or staleness to drive prioritization).

- **Actionable KPIs:** Always surface key success metrics (like Total Interviews or Conversion Rates) in top-level metric rows. Ensure these KPIs reflect **true historical progression** (i.e., counting entities that *ever* reached a milestone) rather than just current snapshot states.

- **Auto-Restart Local Streamlit Server:** After making code changes to a Streamlit application, ALWAYS kill any stale server process running on port 8501 (`kill -9 $(lsof -t -i:8501) 2>/dev/null`) and restart the Streamlit dev server in the background (`.venv/bin/streamlit run src/myproject/main.py --server.port 8501`) to ensure the local application instance is fresh and responsive.

