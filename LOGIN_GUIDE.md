# Login & Logout System — Usage Guide

## 🎯 Overview

The system now supports two modes:

### 1. **Local Mode** (Development with .env)
- API key in `.env` file
- **No login page** — goes straight to setup
- Logout button **hidden**
- For developers/instructors

### 2. **Hosted Mode** (Render/Hugging Face)
- No `.env` file (or empty `OPENAI_API_KEY`)
- **Login page shown** — users provide name + API key
- Logout button **visible** in top-right corner
- Each user pays for their own OpenAI usage

---

## 🚀 Running Locally

### With API Key (Skip Login):
```bash
# Make sure .env has OPENAI_API_KEY
python challenge.py
# or
python app.py
```

### Without API Key (Test Login Page):
```bash
# Temporarily hide .env
mv .env .env.backup

# Run the app
python app.py

# You'll see the login page!
# Enter name + API key to continue

# Restore .env when done
mv .env.backup .env
```

---

## 🌐 Deploying to Render

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for full guide.

**Quick steps:**
1. Push code to GitHub
2. Connect Render to your repo
3. Render auto-detects `render.yaml`
4. Deploy! 🚀

**Don't add `OPENAI_API_KEY` to Render** — let users provide their own!

---

## 🔐 How Login Works

### Login Page Components:
- **Name field**: Student's name (shown in header)
- **API Key field**: OpenAI API key (sk-proj-...)
- **Continue button**: Validates key and proceeds

### Validation:
- Checks format (must start with `sk-`)
- Makes test call to OpenAI API
- Shows error if invalid/no quota
- Sets key in environment on success

### Logout:
- **Button location**: Top-right corner (after login)
- **Action**: Clears API key, returns to login page
- **Note**: Refresh won't logout — must click button explicitly

---

## 🔄 Auto-Detection Logic

```python
has_env_key = bool(os.getenv("OPENAI_API_KEY"))

if has_env_key:
    # Show setup page directly
    # Hide login page
    # Hide logout button
else:
    # Show login page
    # Hide setup page
    # Show logout button after login
```

---

## 📝 Files Modified

- ✅ `student_interface.py` — Added `validate_openai_key()`, login page, logout button
- ✅ `challenge.py` — Made API key optional for GUI mode
- ✅ `app.py` — New entry point for hosting (uses port from env)
- ✅ `render.yaml` — Render configuration
- ✅ `RENDER_DEPLOYMENT.md` — Deployment guide

---

## ⚠️ Important Notes

### For Local Users:
- Keep your `.env` file **private** (in `.gitignore`)
- Never commit API keys to git!

### For Hosted Users:
- Each student needs their own OpenAI API key
- Keys are **session-only** (not stored)
- Logout clears the key from memory

### Cost Management:
- **Hosted mode**: Each user pays for their own usage
- **Local mode**: You pay (instructor/developer)
- **Recommendation**: Use hosted mode for courses/public access

---

## 🧪 Testing

### Test Login Flow:
```bash
# 1. Hide .env to force login page
mv .env .env.backup

# 2. Run app
python app.py

# 3. Try login with:
#    - Empty fields → error
#    - Invalid key → error  
#    - Valid key → success!

# 4. Test logout button
#    - Click logout → returns to login page
#    - Login again → works!

# 5. Restore .env
mv .env.backup .env
```

### Test Local Mode:
```bash
# With .env present
python challenge.py

# Should skip login page entirely
# Go straight to setup page
# No logout button visible
```

---

## 🐛 Troubleshooting

**Q: Login page not showing?**  
A: Check that `OPENAI_API_KEY` is not in `.env` or environment

**Q: Logout button not visible?**  
A: It only appears after successful login (hosted mode)

**Q: "API key valid but no quota"?**  
A: User needs to add billing/credits at platform.openai.com/billing

**Q: Refresh goes back to setup page?**  
A: Known Gradio limitation — use explicit logout button instead

**Q: Can I force login page even with .env?**  
A: Yes! Temporarily comment out `OPENAI_API_KEY` in `.env`

---

## 📚 Related Documentation

- [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) — How to deploy to Render
- [add_login.md](add_login.md) — Detailed implementation notes
- [README.md](README.md) — Main project documentation
