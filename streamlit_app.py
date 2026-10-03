"""Root launcher for the student dashboard."""

import runpy
import sys
from pathlib import Path


dashboard_directory = Path(__file__).parent / "student-dashboard"
sys.path.insert(0, str(dashboard_directory))
runpy.run_path(str(dashboard_directory / "app.py"), run_name="__main__")