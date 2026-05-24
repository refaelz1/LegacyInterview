"""
app.py — MINIMAL TEST VERSION

Testing basic Gradio page transitions on HF Spaces.
This version uses minimal_test.py instead of the full student_interface.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("MINIMAL TEST - Testing Page Transitions")
logger.info("=" * 80)

import gradio as gr
from minimal_test import demo

logger.info("✅ Minimal demo imported successfully!")

# For local/Render/HF deployment
if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    logger.info(f"📍 Launching on 0.0.0.0:{port}...")
    
    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=False,
            inbrowser=False,
            show_error=True,
        )
        logger.info("✅ Demo started!")
    except Exception as e:
        logger.error(f"❌ Launch failed: {e}", exc_info=True)
        raise


