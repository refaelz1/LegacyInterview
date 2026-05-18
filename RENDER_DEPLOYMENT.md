# Render Deployment Guide

## Quick Start

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Add login system and Render support"
   git push origin main
   ```

2. **Create Render Account**:
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Deploy**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Click "Create Web Service"

4. **Optional: Add API Key for Local Users**:
   - Go to Environment tab
   - Add `OPENAI_API_KEY` if you want local development without login
   - Leave empty to require all users to login with their own keys

## How It Works

- **With API key in .env**: Login page is skipped (local development)
- **Without API key**: Users see login page and provide their own OpenAI API key
- **Logout button**: Appears after login, allows switching accounts

## Files for Render

- `app.py` - Main entry point for hosted environment
- `render.yaml` - Render configuration (includes git installation)
- `Aptfile` - System packages (git required for cloning repos)
- `requirements.txt` - Python dependencies
- `start.sh` - Alternative startup script

## Important: Git Requirement

This project clones GitHub repositories dynamically at runtime using GitPython. 
The `Aptfile` ensures git is installed in the Render container.

## Environment Variables

- `PORT` - Automatically set by Render (default: 10000)
- `OPENAI_API_KEY` - Optional, only for skipping login page

## Cost Notes

When users provide their own API keys:
- Each user pays for their own OpenAI usage
- Your hosting cost is only Render's free tier (or paid plan)
- No surprise OpenAI bills!

## Testing Locally

Test the hosted mode (with login page):
```bash
# Temporarily rename .env to disable auto-detection
mv .env .env.backup
python app.py
# Restore .env when done
mv .env.backup .env
```

## Troubleshooting

**Login page not showing?**
- Check that `OPENAI_API_KEY` is NOT set in Render environment

**"API key valid but no quota"?**
- User needs to add credits to their OpenAI account at platform.openai.com/billing

**"git: command not found" or clone errors?**
- Ensure `Aptfile` is committed to your repo
- Render should automatically install git from Aptfile
- Check build logs to verify git installation

**Timeout errors?**
- Render free tier may timeout on long operations (cloning + bug injection can take 1-2 min)
- Consider upgrading to paid plan for production use
- Free tier has 15-minute request timeout
