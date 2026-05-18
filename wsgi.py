#!/usr/bin/env python3
"""
wsgi.py — Gunicorn WSGI wrapper for Gradio

This is a workaround for Render's auto-detection.
Render insists on running 'gunicorn app:app' but Gradio doesn't support WSGI.

Solution: This file makes gunicorn launch python app.py as a subprocess.
"""

import os
import sys
import subprocess

# When gunicorn imports this, we launch the real app and exit
if __name__ != "__main__":
    print("🔧 Gunicorn detected - launching python app.py instead...")
    subprocess.run([sys.executable, "app.py"])
    sys.exit(0)

# This should never be reached, but just in case:
def application(environ, start_response):
    """Dummy WSGI application that should never be called."""
    status = '500 Internal Server Error'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b'Error: Use python app.py directly, not WSGI']

app = application
