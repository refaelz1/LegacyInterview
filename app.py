"""
app.py — Simplified entry point for hosting platforms (Render, Hugging Face, etc.)

This file launches the full interface with login page support.
No API key required — users provide their own via the login page.

For Hugging Face Spaces: demo object is created at module level
For Render/local: can run with python app.py
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

# Create demo at module level for Hugging Face Spaces
print("🚀 Initializing Legacy Code Challenge...")
has_key = bool(os.getenv("OPENAI_API_KEY"))

if has_key:
    print("✅ API key detected in environment — skipping login page")
else:
    print("🔐 No API key found — login page will be shown")

demo = student_interface.create_full_interface()
print("✅ Interface created successfully!")

# For local/Render deployment
if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    print(f"📍 Server will listen on 0.0.0.0:{port}")
    print(f"🌐 Launching Gradio on 0.0.0.0:{port}...")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        inbrowser=False,
        show_error=True,
    )
    
    print("✅ Gradio server started successfully!")
