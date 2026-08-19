#!/usr/bin/env python3
"""WSGI entrypoint.

Vercel's Python runtime looks for a Flask `app` in a root-level entrypoint;
this is it. Local development can also run `python app.py`.
"""

from Frontend.app import app

if __name__ == "__main__":
    from Backend.config.settings import settings

    app.run(host="0.0.0.0", port=settings.frontend_port)
