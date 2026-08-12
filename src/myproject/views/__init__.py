import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_myproject_dir = os.path.dirname(_this_dir)
_src_dir = os.path.dirname(_myproject_dir)

for _p in [_src_dir, _myproject_dir, _this_dir]:
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)

from .overview_analytics import render_overview_analytics_view
from .job_tracker import render_job_tracker_view
from .ats_scorer import render_ats_scorer_view
from .admin_tools import render_admin_tools_view
from .discovered_jobs_view import render_discovered_jobs_view
from .weekly_digest_view import render_weekly_digest_view

__all__ = [
    "render_overview_analytics_view",
    "render_job_tracker_view",
    "render_ats_scorer_view",
    "render_admin_tools_view",
    "render_discovered_jobs_view",
    "render_weekly_digest_view",
]
