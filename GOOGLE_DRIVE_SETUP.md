# Google Drive Backup Setup Guide
## ================================

Google Drive backup creates detailed submission folders with all files for each student.

## What Gets Saved

Each submission creates a folder in your Drive:
```
📁 Legacy Code Submissions/
  📁 2026-05-19_1430_StudentName_RepoName/
     📄 1_challenge_prompt.md         ← The full challenge description
     📄 2_original_code.py            ← Original code before bugs
     📄 3_buggy_code.py               ← Code with bugs (what student got)
     📄 4_student_solution.py         ← What the student submitted
     📄 5_chat_history.txt            ← Full conversation with AI
     📄 6_summary.json                ← Scores, tests, metadata
```

---

## Setup Instructions

### Step 1: Enable Google Drive API

1. Go to: https://console.cloud.google.com
2. Select your project: **"Legacy Code Challenge"**
3. Navigate to: **APIs & Services** → **Library**
4. Search for: **"Google Drive API"**
5. Click on it → Click **"Enable"**

### Step 2: Create Folder in Google Drive

1. Go to: https://drive.google.com
2. Create a new folder: **"Legacy Code Submissions"**
3. Right-click the folder → **Share**
4. Add your service account email:
   - Open `google-service-account.json`
   - Find `"client_email"` field
   - Copy the email (e.g., `legacy-code-logger@...iam.gserviceaccount.com`)
   - Paste it in the Share dialog
5. Give it **Editor** permissions
6. Click **Share** (uncheck "Notify people")

### Step 3: Get Folder ID

1. Open the folder you just created
2. Look at the URL in your browser:
   ```
   https://drive.google.com/drive/folders/1abc123XYZ456...
                                            ^^^^^^^^^^^^^^^
                                            This is the Folder ID
   ```
3. **Copy the Folder ID** (the part after `/folders/`)

### Step 4: Add to Environment Variables

Add to your `.env` file:
```env
GOOGLE_DRIVE_FOLDER_ID=1abc123XYZ456...
```

---

## Testing Locally

1. Make sure `google-service-account.json` is in the project root
2. Make sure `GOOGLE_DRIVE_FOLDER_ID` is in `.env`
3. Run the test:
   ```bash
   python google_drive_logger.py test
   ```
4. Check your Drive folder - you should see a test submission!

---

## For Render Deployment

The same `google-service-account.json` and environment variables work on Render.

**Already done:**
- ✅ `google-service-account.json` uploaded to Render (Secret Files)
- ✅ `GOOGLE_SHEET_ID` in Render Environment Variables

**To add:**
- Add `GOOGLE_DRIVE_FOLDER_ID` to Render Environment Variables:
  1. Render Dashboard → Settings → Environment
  2. Add environment variable:
     ```
     Key: GOOGLE_DRIVE_FOLDER_ID
     Value: [paste your folder ID here]
     ```
  3. Save Changes → Redeploy

---

## What You'll See

After each student submits:
- ✅ **Google Sheets** - New row in dashboard (real-time overview)
- ✅ **Google Drive** - New folder with 6 files (detailed backup)

Both update automatically and persist forever!

---

## Security Notes

- The service account can only access:
  - The specific Sheet you shared with it
  - The specific Drive folder you shared with it
- No access to your other files
- Both are already restricted by API scope (Sheets + Drive only)
