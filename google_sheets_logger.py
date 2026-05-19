"""
google_sheets_logger.py — Optional Google Sheets integration for submission logging

This module provides automatic logging of student submissions to Google Sheets.
If not configured (no GOOGLE_SHEET_ID), it silently fails and the system continues normally.
"""

import os
from datetime import datetime
from typing import Optional


def log_to_google_sheets(
    student_name: str,
    repo_url: str,
    hints_used: int,
    score: int,
    total_tests: int,
    passed_tests: int,
    all_passed: bool,
    student_code: str,
    chat_history: list,
) -> bool:
    """
    Log submission to Google Sheets.
    
    Returns True if successful, False otherwise.
    If Google Sheets is not configured, returns False silently.
    """
    
    # Check if Google Sheets is configured
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        return False  # Silently skip if not configured
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Check if service account file exists
        service_account_file = "google-service-account.json"
        if not os.path.exists(service_account_file):
            print("⚠️ Google Sheets: service account file not found")
            return False
        
        # Authenticate
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Open the sheet
        sheet = client.open_by_key(sheet_id).sheet1
        
        # Prepare row data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Truncate long fields for readability
        code_preview = student_code[:200] + "..." if len(student_code) > 200 else student_code
        chat_summary = f"{len(chat_history)} messages" if chat_history else "No chat"
        
        row = [
            timestamp,
            student_name or "Anonymous",
            repo_url,
            score,
            hints_used,
            f"{passed_tests}/{total_tests}",
            "✅" if all_passed else "❌",
            code_preview,
            chat_summary,
        ]
        
        # Append row
        sheet.append_row(row)
        
        print(f"✅ Logged to Google Sheets: {student_name} - Score: {score}")
        return True
        
    except ImportError:
        print("⚠️ Google Sheets: gspread not installed (pip install gspread google-auth)")
        return False
    except Exception as e:
        print(f"⚠️ Google Sheets logging failed: {e}")
        return False


def initialize_sheet_headers(sheet_id: Optional[str] = None) -> bool:
    """
    Initialize Google Sheet with headers if it's empty.
    Call this once to set up the sheet.
    """
    
    sheet_id = sheet_id or os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("❌ GOOGLE_SHEET_ID not set")
        return False
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        service_account_file = "google-service-account.json"
        if not os.path.exists(service_account_file):
            print(f"❌ Service account file not found: {service_account_file}")
            return False
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(sheet_id).sheet1
        
        # Check if already has headers
        if sheet.row_count > 0 and sheet.row_values(1):
            print("✅ Sheet already has headers")
            return True
        
        # Add headers
        headers = [
            "Timestamp",
            "Student Name",
            "Repository",
            "Score",
            "Hints Used",
            "Tests Passed",
            "All Passed?",
            "Code Preview",
            "Chat Summary"
        ]
        
        sheet.append_row(headers)
        
        # Format headers (bold)
        sheet.format("A1:I1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
        })
        
        print("✅ Headers initialized!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize headers: {e}")
        return False


# CLI tool for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        # Initialize headers
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            print("Set GOOGLE_SHEET_ID in .env first!")
            sys.exit(1)
        
        success = initialize_sheet_headers(sheet_id)
        sys.exit(0 if success else 1)
    
    else:
        # Test logging
        print("Testing Google Sheets logging...")
        success = log_to_google_sheets(
            student_name="Test Student",
            repo_url="https://github.com/test/repo",
            hints_used=2,
            score=85,
            total_tests=10,
            passed_tests=8,
            all_passed=False,
            student_code="def test(): pass",
            chat_history=[{"role": "user", "content": "test"}],
        )
        
        if success:
            print("✅ Test successful!")
        else:
            print("❌ Test failed - check configuration")
