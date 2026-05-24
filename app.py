"""
app.py — Simplified entry point for hosting platforms (Render, Hugging Face, etc.)

This file launches the full interface with login page support.
No API key required — users provide their own via the login page.

For Hugging Face Spaces: demo object is created at module level
For Render/local: can run with python app.py
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging BEFORE everything else
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load .env if it exists (for local development)
load_dotenv()

# Apply proxy settings from .env if defined
if os.getenv("http_proxy"):
    logger.info(f"Setting http_proxy: {os.getenv('http_proxy')}")
    os.environ["http_proxy"] = os.getenv("http_proxy")
if os.getenv("https_proxy"):
    logger.info(f"Setting https_proxy: {os.getenv('https_proxy')}")
    os.environ["https_proxy"] = os.getenv("https_proxy")
if os.getenv("no_proxy"):
    os.environ["no_proxy"] = os.getenv("no_proxy")

import gradio as gr
import student_interface

# Create demo at module level for Hugging Face Spaces
logger.info("🚀 Initializing Legacy Code Challenge...")
has_key = bool(os.getenv("OPENAI_API_KEY"))

if has_key:
    logger.info("✅ API key detected in environment — skipping login page")
else:
    logger.info("🔐 No API key found — login page will be shown")

try:
    demo = student_interface.create_full_interface()
    logger.info("✅ Interface created successfully!")
except Exception as e:
    logger.error(f"❌ Failed to create interface: {e}", exc_info=True)
    raise

# For local/Render deployment
if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    logger.info(f"📍 Server will listen on 0.0.0.0:{port}")
    logger.info(f"🌐 Launching Gradio on 0.0.0.0:{port}...")
    
    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=False,
            inbrowser=False,
            show_error=True,
        )
        logger.info("✅ Gradio server started successfully!")
    except Exception as e:
        logger.error(f"❌ Launch failed: {e}", exc_info=True)
        raise

