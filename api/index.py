#!/usr/bin/env python3
"""ASGI entrypoint for the deployed API.

Vercel's Python runtime serves an `app` it finds in a file under `api/`; this is
that file. Everything it exposes lives in Backend/api/main.py — nothing but the
import belongs here.

The frontend is a separate deployment (see web/) and calls this over HTTP from
its server, never from the browser.
"""

import sys
from pathlib import Path

# The function's working directory is the repo root on Vercel and could be
# anywhere locally, so make the package importable either way.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Backend.api.main import app  # noqa: E402,F401
