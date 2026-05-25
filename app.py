"""
app.py — Entry point using minimal_test.py (Tabs-based navigation)

This version uses Tabs instead of Columns for better production compatibility.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load .env if it exists
load_dotenv()

# Apply proxy settings
if os.getenv("http_proxy"):
    os.environ["http_proxy"] = os.getenv("http_proxy")
if os.getenv("https_proxy"):
    os.environ["https_proxy"] = os.getenv("https_proxy")
if os.getenv("no_proxy"):
    os.environ["no_proxy"] = os.getenv("no_proxy")

logger.info("🚀 Launching Legacy Code Challenge (Full featured Tabs version)...")

from student_interface_tabs import demo

logger.info("✅ Demo imported successfully!")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    logger.info(f"📍 Launching on 0.0.0.0:{port}...")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        inbrowser=False,
        show_error=True,
    )

