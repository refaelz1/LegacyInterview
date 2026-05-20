"""
git_submissions_logger.py — Push detailed submission reports to Git repository

Creates a comprehensive backup folder for each submission and commits to Git:
- Original prompt/challenge
- Original code (before bugs)
- Buggy code (what student received)
- Student's solution
- Full chat history
- Summary JSON

Each submission is automatically committed and pushed to a dedicated Git repository.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


def push_submission_to_git(
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
    Create submission folder and push to Git repository.
    
    Structure:
    submissions/
      └── 2026-05-20_1430_StudentName_RepoName/
          ├── 1_challenge_prompt.md
          ├── 2_original_code.py
          ├── 3_buggy_code.py
          ├── 4_student_solution.py
          ├── 5_chat_history.txt
          └── 6_summary.json
    
    Returns True if successful, False otherwise.
    """
    
    # Check if Git submissions repo is configured
    submissions_repo = os.getenv("SUBMISSIONS_REPO_URL")
    git_token = os.getenv("SUBMISSIONS_GIT_TOKEN")
    
    if not submissions_repo:
        print("⚠️ Git Submissions: SUBMISSIONS_REPO_URL not configured in .env")
        return False
    
    try:
        # Create submissions directory if it doesn't exist
        submissions_dir = Path("submissions_backup")
        submissions_dir.mkdir(exist_ok=True)
        
        # Initialize Git repo if needed
        git_dir = submissions_dir / ".git"
        if not git_dir.exists():
            print("📂 Initializing Git repository...")
            subprocess.run(
                ["git", "init"],
                cwd=submissions_dir,
                check=True,
                capture_output=True
            )
            
            # Configure remote with token if available
            if git_token:
                # Format: https://TOKEN@github.com/user/repo.git
                repo_with_token = submissions_repo.replace("https://", f"https://{git_token}@")
                subprocess.run(
                    ["git", "remote", "add", "origin", repo_with_token],
                    cwd=submissions_dir,
                    check=True,
                    capture_output=True
                )
            else:
                subprocess.run(
                    ["git", "remote", "add", "origin", submissions_repo],
                    cwd=submissions_dir,
                    check=True,
                    capture_output=True
                )
            
            # Pull existing commits if repo exists
            try:
                subprocess.run(
                    ["git", "pull", "origin", "main"],
                    cwd=submissions_dir,
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                # Repo might be empty, that's OK
                pass
            
            print("✅ Git repository initialized")
        
        # Create submission folder name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        folder_name = f"{timestamp}_{student_name}_{repo_name}"
        
        submission_folder = submissions_dir / folder_name
        submission_folder.mkdir(exist_ok=True)
        print(f"📁 Creating submission: {folder_name}")
        
        # Prepare files to write
        files_to_write = [
            ("1_challenge_prompt.md", challenge_prompt),
            ("2_original_code.py", f"# Original code (before bugs)\n# Target file: {target_file}\n\n{original_code}"),
            ("3_buggy_code.py", f"# Buggy code (what student received)\n# Target file: {target_file}\n\n{buggy_code}"),
            ("4_student_solution.py", f"# Student's solution\n# Target file: {target_file}\n\n{student_code}"),
            ("5_chat_history.txt", _format_chat_history(chat_history)),
            ("6_summary.json", json.dumps({
                'student_name': student_name,
                'repository': repo_url,
                'timestamp': datetime.now().isoformat(),
                'score': score,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                'hints_used': hints_used,
                'target_file': target_file,
            }, ensure_ascii=False, indent=2)),
        ]
        
        # Write all files
        print(f"📝 Writing {len(files_to_write)} files...")
        for filename, content in files_to_write:
            file_path = submission_folder / filename
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✅ {filename}")
        
        # Git add, commit, push
        print("📤 Committing to Git...")
        subprocess.run(
            ["git", "add", "."],
            cwd=submissions_dir,
            check=True,
            capture_output=True
        )
        
        commit_message = f"Add submission: {student_name} - {repo_name} ({score}/{total_tests*10} pts)"
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=submissions_dir,
            check=True,
            capture_output=True
        )
        
        print("🚀 Pushing to GitHub...")
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=submissions_dir,
            check=True,
            capture_output=True,
            timeout=30
        )
        
        print(f"✅ Pushed to Git: {folder_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git command failed: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        print(f"⚠️ Git submission failed: {type(e).__name__}: {e}")
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
    from dotenv import load_dotenv
    
    # Load .env file for testing
    load_dotenv()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing Git submissions integration...")
        
        submissions_repo = os.getenv("SUBMISSIONS_REPO_URL")
        if not submissions_repo:
            print("❌ SUBMISSIONS_REPO_URL not set in .env")
            sys.exit(1)
        
        success = push_submission_to_git(
            student_name="Test_Student",
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
            print("✅ Test push successful!")
        else:
            print("❌ Test push failed")
            sys.exit(1)
