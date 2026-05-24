"""
Quick launcher for existing workspace - no pipeline run needed!
Usage: python launch_existing.py workspaces/inflection
"""
import argparse
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set.")
    sys.exit(1)

from student_interface import create_interface


def main():
    parser = argparse.ArgumentParser(description="Launch interface for existing workspace")
    parser.add_argument("workspace", help="Path to workspace folder (e.g., workspaces/inflection)")
    parser.add_argument("--name", default="Student", help="Student name")
    parser.add_argument("--timer", type=int, default=0, help="Timer in minutes (0 = no timer)")
    parser.add_argument("--port", type=int, default=7860, help="Port (default: 7860)")
    args = parser.parse_args()

    print(f"\n🚀 Launching interface for workspace: {args.workspace}")
    print(f"   Name: {args.name}")
    print(f"   Port: http://localhost:{args.port}\n")

    demo = create_interface(args.workspace, student_name=args.name, timer_minutes=args.timer)
    
    # Set share=True to get a public URL (valid for 72 hours)
    demo.launch(server_port=args.port, share=True)


if __name__ == "__main__":
    main()
