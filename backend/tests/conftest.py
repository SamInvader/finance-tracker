import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND.parent
for path in (PROJECT_ROOT, BACKEND):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
