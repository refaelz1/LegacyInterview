"""
app.py — Simplified entry point for hosting platforms (Render, Hugging Face, etc.)

This file launches the full interface with login page support.
No API key required — users provide their own via the login page.

IMPORTANT: This is a Gradio application, NOT a WSGI app.
Do not use gunicorn! Run directly with: python app.py
"""

import os
from dotenv import load_dotenv

# Load .env if it exists (for local development)
load_dotenv()

# Apply proxy settings from .env if defined
if os.getenv("http_proxy"):
    os.environ["http_proxy"] = os.getenv("http_proxy")
if os.getenv("https_proxy"):
    os.environ["https_proxy"] = os.getenv("https_proxy")
if os.getenv("no_proxy"):
    os.environ["no_proxy"] = os.getenv("no_proxy")

import gradio as gr
import student_interface


# Create the Gradio interface globally for uvicorn
port = int(os.getenv("PORT", "7860"))
has_key = bool(os.getenv("OPENAI_API_KEY"))

print(f"\n🚀 Starting Legacy Code Challenge on port {port}...")
print(f"📍 Server will listen on 0.0.0.0:{port}")

if has_key:
    print("✅ API key detected in environment — skipping login page")
else:
    print("🔐 No API key found — login page will be shown")

demo = student_interface.create_full_interface()

# Expose the FastAPI/ASGI app for uvicorn
app = demo.app


# For direct Python execution (development)
def main() -> None:
    """Launch the full interface with auto-detected login page."""
    
    print(f"🌐 Launching Gradio on 0.0.0.0:{port}...")
    
    demo.launch(
        server_name="0.0.0.0",  # Listen on all interfaces for hosting
        server_port=port,
        share=False,  # Render provides its own URL
        inbrowser=False,  # Don't open browser on server
        theme=gr.themes.Base(),
        css=student_interface._CSS,
        js=student_interface._JS,
        show_error=True,  # Show detailed errors in Render logs
    )
    
    print("✅ Gradio server started successfully!")


if __name__ == "__main__":
    main()
