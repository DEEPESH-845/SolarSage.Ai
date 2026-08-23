#!/usr/bin/env python3
"""ASGI entrypoint for the deployed API.

Vercel's Python runtime looks for an ASGI `app` in a root-level `main.py` (or
`app.py` / `index.py`) and serves *every* path through it, which is what makes
`/health`, `/overview` and the rest resolve in production. The application
itself lives in Backend/api/main.py — nothing but the import belongs here.

Placing it here rather than under `api/` is deliberate: a module under `api/` is
treated as one function bound to its own path, so requests for `/health` never
reach the router.

The console is a separate deployment (see web/) and calls this over HTTPS from
its server, never from the browser.
"""

from Backend.api.main import app  # noqa: F401

__all__ = ["app"]
