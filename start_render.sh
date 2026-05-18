#!/bin/bash
# Render startup script - use uvicorn for ASGI support
echo "🚀 Starting with uvicorn (ASGI server for Gradio/FastAPI)..."
exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}
