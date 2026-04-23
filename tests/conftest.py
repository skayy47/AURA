"""pytest configuration — adds the project root to sys.path."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure `engines`, `utils`, `state` etc. are importable when running
# pytest from any working directory.
sys.path.insert(0, str(Path(__file__).parent.parent))
