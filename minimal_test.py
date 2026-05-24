"""Legacy Code Challenge - Tabs version (production-ready)"""
import gradio as gr
import os
import logging
import json
from pathlib import Path
from io import StringIO
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import required modules from student_interface
from orchestrator.scoring import evaluate_submission

# ── ChallengeState ──────────────────────────────────────────────────────────

class ChallengeState:
    """Loads challenge data from challenge_state.json."""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        state_file = self.workspace / "challenge_state.json"
        if not state_file.exists():
            raise FileNotFoundError(f"challenge_state.json not found in {workspace_path}")
        
        with open(state_file, encoding="utf-8") as f:
            data = json.load(f)
        
        self.github_url = data.get("github_url", "")
        self.target_file = data.get("target_file", "")
        self.original_code = data.get("original_code", "")
        self.sabotaged_code = data.get("sabotaged_code", "")
        self.bug_func_name = data.get("bug_func_name", "")
        self.bug_func_names = data.get("bug_func_names", [])
    
    @property
    def target_path(self) -> Path:
        return self.workspace / self.target_file
    
    def read_target(self) -> str:
        if self.target_path.exists():
            return self.target_path.read_text(encoding="utf-8")
        return self.sabotaged_code
    
    def readme(self) -> str:
        readme_path = self.workspace / "STUDENT_README.md"
        if readme_path.exists():
            return readme_path.read_text(encoding="utf-8")
        return "# Challenge\n\nREADME not found."

# ── Pipeline function ───────────────────────────────────────────────────────

def _run_pipeline(github_url: str, nesting_level: int, num_bugs: int,
                  refactoring_enabled: bool = False, debug_mode: bool = False) -> str:
    """Invoke the architect pipeline and return workspace path."""
    from architect.graph import build_graph
    
    graph = build_graph()
    result = graph.invoke({
        "github_url": github_url,
        "nesting_level": nesting_level,
        "refactoring_enabled": refactoring_enabled,
        "debug_mode": debug_mode,
        "num_bugs": num_bugs,
        "clone_path": "",
        "target_file": "",
        "original_code": "",
        "sabotaged_code": "",
        "function_name": "",
        "test_cases": [],
        "public_tests": [],
        "secret_tests": [],
        "candidate_files": [],
        "bug_func_name": "",
        "call_chain": {},
    })
    
    workspace_path = result["clone_path"]
    target_file_rel = result.get("target_file", "")
    actual_sabotaged_code = result.get("sabotaged_code", "")
    
    # Persist challenge_state.json
    challenge_state = {
        "github_url": github_url,
        "workspace_path": workspace_path,
        "target_file": target_file_rel,
        "original_code": result.get("original_code", ""),
        "sabotaged_code": actual_sabotaged_code,
        "function_name": result.get("function_name", ""),
        "bug_func_name": result.get("bug_func_name", ""),
        "bug_func_names": result.get("bug_func_names", []),
        "test_cases": result.get("test_cases", []),
        "public_tests": result.get("public_tests", []),
        "secret_tests": result.get("secret_tests", []),
        "nesting_level": nesting_level,
        "refactoring_enabled": refactoring_enabled,
        "debug_mode": debug_mode,
    }
    
    state_path = Path(workspace_path) / "challenge_state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(challenge_state, f, indent=2, ensure_ascii=False)
    
    return workspace_path

# ── UI ──────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Legacy Code Challenge", theme=gr.themes.Soft()) as demo:
    
    # Hidden state
    workspace_state = gr.State("")
    
    with gr.Tabs() as tabs:
        # Tab 0: Login
        with gr.Tab("🔐 Login", id=0):
            gr.Markdown("# 🔐 Welcome to Legacy Code Challenge")
            name_input = gr.Textbox(label="Your Name", placeholder="e.g. Alice")
            api_input = gr.Textbox(label="OpenAI API Key", placeholder="sk-proj-...", type="password")
            login_btn = gr.Button("Continue ➡️", variant="primary", size="lg")
        
        # Tab 1: Setup
        with gr.Tab("⚙️ Setup", id=1):
            gr.Markdown("# ⚙️ Setup Challenge")
            url_input = gr.Textbox(label="GitHub URL", value="https://github.com/mahmoud/boltons")
            with gr.Row():
                num_bugs = gr.Slider(1, 5, value=3, step=1, label="Number of Bugs")
                nesting_slider = gr.Slider(1, 6, value=2, step=1, label="Nesting Level (call-chain depth)")
            with gr.Row():
                refactoring_check = gr.Checkbox(label="🔀 Enable Refactoring", value=False)
                debug_check = gr.Checkbox(label="🐞 Debug Mode", value=False)
            start_btn = gr.Button("Start Challenge ➡️", variant="primary", size="lg")
            status_md = gr.Markdown("")
        
        # Tab 2: Challenge
        with gr.Tab("💻 Challenge", id=2):
            gr.Markdown("# 💻 Fix the Code")
            
            with gr.Tabs() as challenge_tabs:
                # Sub-tab: README
                with gr.Tab("📋 Challenge", id=0):
                    readme_md = gr.Markdown("Challenge description will appear here...")
                
                # Sub-tab: Code Editor
                with gr.Tab("💻 Code Editor", id=1):
                    code_box = gr.Textbox(label="Code", lines=20, interactive=True)
                
                # Sub-tab: Chat/Hints (placeholder for now)
                with gr.Tab("💬 Chat", id=2):
                    gr.Markdown("💡 Chat for hints will be available here...")
            
            submit_btn = gr.Button("Submit ➡️", variant="primary", size="lg")
        
        # Tab 3: Results
        with gr.Tab("🎯 Results", id=3):
            gr.Markdown("# 🎯 Evaluation Results")
            score_html = gr.HTML("")
            tests_html = gr.HTML("")
    
    # Event handlers
    def on_login(name, api_key):
        if not name or not api_key:
            return gr.Tabs(selected=0)
        os.environ["OPENAI_API_KEY"] = api_key
        logger.info(f"User logged in: {name}")
        return gr.Tabs(selected=1)
    
    def on_start(url, bugs):
        logger.info(f"Starting: {url}, bugs={bugs}")
        yield gr.Tabs(selected=1), "⏳ Creating challenge...", "", "", ""
        
        try:
            workspace = _run_pipeline(url.strip(), nesting_level=2, num_bugs=int(bugs))
            cs = ChallengeState(workspace)
            code = cs.read_target()
            readme = cs.readme()
            yield gr.Tabs(selected=2), f"✅ Ready! File: {cs.target_file}", readme, code, workspace
        except Exception as exc:
            logger.error(f"Pipeline failed: {exc}", exc_info=True)
            yield gr.Tabs(selected=1), f"❌ Error: {exc}", "", "", ""
    
    def on_submit(workspace):
        logger.info(f"Submit: workspace={workspace}")
        
        # Move to results tab immediately
        yield gr.Tabs(selected=3), "<p style='text-align:center;padding:40px;'>⏳ Running tests...</p>", ""
        
        try:
            if not workspace:
                yield gr.Tabs(selected=3), "❌ No challenge loaded", ""
                return
            
            cs = ChallengeState(workspace)
            submitted_code = cs.read_target()
            
            result = evaluate_submission(
                workspace_path=workspace,
                student_code=submitted_code,
                original_code=cs.original_code,
                bug_func_name=cs.bug_func_name,
                hints_used=0,
                sabotaged_code=cs.sabotaged_code,
                target_file=str(cs.target_path),
                bug_func_names=cs.bug_func_names,
            )
            
            score = result.get("total_score", 0)
            passed = result.get("passed", 0)
            total = result.get("total_tests", 0)
            
            score_html_content = f"""
            <div style='padding:30px;background:#e8f5e9;border-radius:10px;text-align:center;'>
                <h1 style='color:green;margin:0;'>Score: {score}/100</h1>
                <p style='font-size:1.2em;margin-top:10px;'>✅ {passed}/{total} tests passed</p>
            </div>
            """
            
            tests_output = result.get("test_output", "No test output")
            tests_html_content = f"<pre style='background:#f5f5f5;padding:20px;border-radius:5px;'>{tests_output}</pre>"
            
            yield gr.Tabs(selected=3), score_html_content, tests_html_content
            
        except Exception as exc:
            logger.error(f"Submission failed: {exc}", exc_info=True)
            yield gr.Tabs(selected=3), f"❌ Error: {exc}", ""
    
    # Wire events
    login_btn.click(on_login, inputs=[name_input, api_input], outputs=[tabs])
    start_btn.click(on_start, inputs=[url_input, num_bugs], outputs=[tabs, status_md, readme_md, code_box, workspace_state])
    submit_btn.click(on_submit, inputs=[workspace_state], outputs=[tabs, score_html, tests_html])

demo.queue()

if __name__ == "__main__":
    demo.launch()
