"""Rebuild planning dashboards and apply the shared presentation layer."""
from pathlib import Path
import runpy
root=Path(__file__).resolve().parent
for script in ['build_disney.py','build_reliability.py','refresh_app.py','build_trip.py']:
    runpy.run_path(str(root/script))
print('Built Park Atlas dashboards')
