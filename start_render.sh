#!/bin/bash
# Render startup script - force python app.py (NOT gunicorn!)
echo "🚀 Starting with python app.py (unbuffered output)..."
exec python -u app.py
