#!/bin/bash

# Start script for hosting platforms (Render, Heroku, etc.)

echo "🚀 Starting Legacy Code Challenge..."

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Launch the interface
echo "🌐 Launching Gradio interface..."
python main.py
