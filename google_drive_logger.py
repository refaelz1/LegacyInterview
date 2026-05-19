"""
google_drive_logger.py — Upload detailed submission reports to Google Drive

Creates a comprehensive backup folder for each submission with:
- Original prompt/challenge
- Original code (before bugs)
- Buggy code (what student received)
- Student's solution
- Full chat history
- Summary JSON

NOTE: If running on Intel network with proxy, make sure http_proxy and https_proxy
are set in environment variables. The Google API client will use them automatically.
"""

import os
import json
from datetime import datetime
from typing import Optional
from io import BytesIO


def upload_submission_to_drive(
    student_name: str,
    repo_url: str,
    original_code: str,
    buggy_code: str,
    student_code: str,
    chat_history: list,
    score: int,
    total_tests: int,
    passed_tests: int,
    hints_used: int,
    challenge_prompt: str,
    target_file: str,
) -> bool:
    """
    Upload a complete submission backup to Google Drive.
    
    Creates a folder structure:
    Legacy Code Submissions/
      └── 2026-05-19_1430_StudentName_RepoName/
          ├── 1_challenge_prompt.md
          ├── 2_original_code.py
          ├── 3_buggy_code.py
          ├── 4_student_solution.py
          ├── 5_chat_history.txt
          └── 6_summary.json
    
    Returns True if successful, False otherwise.
    """
    
    # Check if Google Drive is configured
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        print("⚠️ Google Drive: GOOGLE_DRIVE_FOLDER_ID not set in environment")
        return False  # Silently skip if not configured
    
    print(f"📂 Google Drive Folder ID: {folder_id[:20]}...")  # First 20 chars only
    
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        from google.oauth2.service_account import Credentials
        
        # Check if service account file exists
        service_account_file = "google-service-account.json"
        if not os.path.exists(service_account_file):
            print("⚠️ Google Drive: service account file not found")
            return False
        
        # Authenticate
        scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        print("✅ Authenticated with service account")
        
        # Build service
        service = build('drive', 'v3', credentials=creds)
        print("✅ Drive service initialized")
        
        # Create submission folder name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        folder_name = f"{timestamp}_{student_name}_{repo_name}"
        
        print(f"📁 Creating folder: {folder_name}")
        
        # Create folder in Drive
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder_id]
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        submission_folder_id = folder.get('id')
        print(f"✅ Folder created: {submission_folder_id}")
        
        # Prepare files to upload
        files_to_upload = [
            {
                'name': '1_challenge_prompt.md',
                'content': challenge_prompt,
                'mime_type': 'text/markdown'
            },
            {
                'name': '2_original_code.py',
                'content': f"# Original code (before bugs)\n# Target file: {target_file}\n\n{original_code}",
                'mime_type': 'text/x-python'
            },
            {
                'name': '3_buggy_code.py',
                'content': f"# Buggy code (what student received)\n# Target file: {target_file}\n\n{buggy_code}",
                'mime_type': 'text/x-python'
            },
            {
                'name': '4_student_solution.py',
                'content': f"# Student's solution\n# Target file: {target_file}\n\n{student_code}",
                'mime_type': 'text/x-python'
            },
            {
                'name': '5_chat_history.txt',
                'content': _format_chat_history(chat_history),
                'mime_type': 'text/plain'
            },
            {
                'name': '6_summary.json',
                'content': json.dumps({
                    'student_name': student_name,
                    'repository': repo_url,
                    'timestamp': datetime.now().isoformat(),
                    'score': score,
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                    'hints_used': hints_used,
                    'target_file': target_file,
                }, ensure_ascii=False, indent=2),
                'mime_type': 'application/json'
            },
        ]
        
        # Upload each file
        print(f"📤 Uploading {len(files_to_upload)} files...")
        for i, file_info in enumerate(files_to_upload, 1):
            try:
                file_metadata = {
                    'name': file_info['name'],
                    'parents': [submission_folder_id]
                }
                
                # Create file content as bytes
                file_content = file_info['content'].encode('utf-8')
                media = MediaIoBaseUpload(
                    BytesIO(file_content),
                    mimetype=file_info['mime_type'],
                    resumable=False  # Simple upload, not resumable
                )
                
                # Upload file
                uploaded_file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                print(f"  ✅ {i}/{len(files_to_upload)}: {file_info['name']}")
            except Exception as file_error:
                print(f"  ❌ {i}/{len(files_to_upload)}: {file_info['name']} - {file_error}")
        
        print(f"✅ Uploaded to Google Drive: {folder_name}")
        return True
        
    except ImportError as e:
        print(f"⚠️ Google Drive: Missing library: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Google Drive upload failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def _format_chat_history(chat_history: list) -> str:
    """Format chat history for text file."""
    if not chat_history:
        return "לא השתמש בהינטים\n"
    
    lines = ["התכתבות מלאה עם הצ'אט\n"]
    lines.append("=" * 60 + "\n\n")
    
    for i, msg in enumerate(chat_history, 1):
        lines.append(f"הינט #{i}\n")
        lines.append("-" * 40 + "\n")
        lines.append(f"שאלה: {msg.get('summary', 'N/A')}\n\n")
        lines.append(f"תשובה:\n{msg.get('response', 'N/A')}\n\n")
        lines.append("=" * 60 + "\n\n")
    
    return "".join(lines)


# CLI testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing Google Drive integration...")
        
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        if not folder_id:
            print("❌ GOOGLE_DRIVE_FOLDER_ID not set in .env")
            sys.exit(1)
        
        success = upload_submission_to_drive(
            student_name="Test Student",
            repo_url="https://github.com/test/repo",
            original_code="def hello():\n    return 'world'",
            buggy_code="def hello():\n    return 'WORLD'",
            student_code="def hello():\n    return 'world'",
            chat_history=[{"summary": "How to fix?", "response": "Check the case"}],
            score=85,
            total_tests=10,
            passed_tests=8,
            hints_used=1,
            challenge_prompt="# Test Challenge\n\nFix the bug!",
            target_file="test.py",
        )
        
        if success:
            print("✅ Test upload successful!")
        else:
            print("❌ Test upload failed")
            sys.exit(1)
