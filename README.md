---
title: Legacy Code Challenge
emoji: 🐛
colorFrom: red
colorTo: pink
sdk: gradio
app_file: app.py
pinned: false
---

# 🐛 Legacy Code Challenge

AI-powered educational tool for debugging legacy code. Students receive buggy code from real GitHub repositories and must fix it with AI assistance.

## Features
- 🔍 Automated bug injection into real codebases
- 🤖 AI-powered hint system (GPT-4o)
- 🧪 Automated testing and scoring
- 📊 Progress tracking via Google Sheets
- 💾 Git-based submission backups

## How to Use
1. Enter your OpenAI API key
2. Choose a GitHub repository (or use default: mahmoud/boltons)
3. Select difficulty level
4. Debug the injected bugs!

## Environment Variables Required
Set these in Hugging Face Spaces Settings:
- `GOOGLE_SHEET_ID` - For logging submissions
- `SUBMISSIONS_REPO_URL` - Git repo for backups
- `SUBMISSIONS_GIT_TOKEN` - Git access token

Note: Users provide their own OpenAI API keys via the login page.
