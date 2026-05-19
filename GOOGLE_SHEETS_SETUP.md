# Google Sheets Integration for Submission Logging
# ================================================

## Setup Instructions

### 1. Create Google Cloud Project
- Go to: https://console.cloud.google.com
- Click "Select a project" → "New Project"
- Name: "Legacy Code Challenge"
- Click "Create"

### 2. Enable Google Sheets API
1. In your project, go to: APIs & Services → Library
2. Search for "Google Sheets API"
3. Click on it → Click "Enable"

### 3. Create Service Account
1. APIs & Services → Credentials
2. Create Credentials → Service Account
3. Service account details:
   - Name: `legacy-code-logger`
   - Description: "Logs student submissions to Google Sheets"
   - Click "Create and Continue"
4. Grant access (optional): Skip this step → Click "Continue"
5. Click "Done"

### 4. Create Service Account Key
1. Click on the service account email you just created
2. Go to "Keys" tab
3. Add Key → Create new key → JSON format
4. Download the JSON file (save as `google-service-account.json`)

**Security Best Practices:**
- ✅ **API Restrictions**: Already done by enabling ONLY Google Sheets API in Step 2
- ✅ **Access Control**: Service account can only access sheets you explicitly share (Step 6)
- ❌ **Application Restrictions** (IP/domain): Not available for service account keys
  - Application restrictions are only for API keys, not service account credentials
  - Service accounts use OAuth 2.0 authentication via JSON key file
- 🔒 **Keep JSON file secure**: Never commit to git, never share publicly

### 5. Create Google Sheet
1. Go to: https://docs.google.com/spreadsheets
2. Create a new spreadsheet
3. Name it: "Legacy Code Submissions"
4. Copy the Sheet ID from URL: 
   ```
   https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
   ```

### 6. Share Sheet with Service Account
1. Open your Google Sheet
2. Click "Share" button (top-right)
3. Add the service account email (find it in `google-service-account.json` under `client_email`)
   - Example: `legacy-code-logger@legacy-code-challenge.iam.gserviceaccount.com`
4. Give it "Editor" permissions
5. Click "Send"

### 7. Setup Files
- Save the downloaded JSON file as `google-service-account.json` in project root
- It's already in `.gitignore` - DO NOT commit it to git!

### 8. Environment Variables (.env)
```env
GOOGLE_SHEET_ID=your_sheet_id_here
# Get from sheet URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
```

## Optional
If you don't want Google Sheets logging:
- Don't set `GOOGLE_SHEET_ID` in .env
- System will work normally without it
- Submissions still saved locally as JSON

## Security Notes
- `google-service-account.json` is in `.gitignore` - **DO NOT commit it to git!**
- The service account can only access sheets you explicitly share with it
- No access to your personal files
- **On Render**: Add the entire JSON content as environment variable or upload via dashboard
- Never share the JSON file publicly

### Security Restrictions Available:
**✅ What IS restricted:**
1. **API Scope**: Only Google Sheets API is enabled (Step 2)
2. **Sheet Access**: Service account can only access sheets you share with it
3. **Permissions**: Service account has Editor role only on shared sheets

**❌ What is NOT available:**
- **Application restrictions** (IP addresses, HTTP referrers, etc.)
  - These apply to API Keys, not Service Account credentials
  - Service accounts use OAuth 2.0, not API keys
  - Security is managed through IAM permissions and sheet sharing

### Why Service Accounts are Secure:
- Even if the JSON file is exposed, attacker can only:
  - Access sheets you explicitly shared with this service account email
  - Use Google Sheets API only (no Gmail, Drive, etc.)
  - Cannot access your personal Google account or files

## Testing
Test locally before deploying:
```bash
python google_sheets_logger.py init
```
This will:
1. Check if credentials are configured
2. Initialize sheet headers
3. Add a test row
