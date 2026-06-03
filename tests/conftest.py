"""pytest configuration — adds AURA-BACKEND to sys.path.

All tests import from the FastAPI stack (AURA-BACKEND/engines/,
AURA-BACKEND/utils/, AURA-BACKEND/state/).  The legacy Streamlit
engines at the repo root are NOT in the import path.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Point at AURA-BACKEND so imports resolve against the FastAPI stack
sys.path.insert(0, str(Path(__file__).parent.parent / "AURA-BACKEND"))
