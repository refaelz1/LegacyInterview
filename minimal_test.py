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

# Import required modules
from orchestrator.scoring import evaluate_submission
from orchestrator.hint_graph import get_hint
from architect.graph import build_graph

# ── Hint Penalty System ──────────────────────────────────────────────────────

PENALTY_TABLE = [0, 2, 6, 12, 20, 30]

_HINT_DECLINES = {
    "no", "nope", "nah", "not now", "nevermind", "never mind",
    "no thanks", "no thank you", "skip", "cancel", "forget it",
    "don't", "dont", "no hint", "stop",
}
_CONFIRMATION_KWS = ["would you like", "shall i", "want me to", "proceed", "penalty to your score"]

def _hint_md(hints_used: int, penalty: int) -> str:
    return (
        f"🤖 **AI Assistant** &nbsp;|&nbsp; "
        f"Hints used: **{hints_used}** &nbsp;|&nbsp; Penalty: **{penalty} pts** &nbsp; "
        f"_(−2 / −6 / −12 / −20 / −30)_"
    )

def _is_decline(msg: str) -> bool:
    m = msg.strip().lower()
    return (
        m in _HINT_DECLINES
        or m.startswith("no ")
        or m.startswith("don't")
        or m.startswith("dont")
        or m.startswith("nope ")
        or m.startswith("nah ")
    )

def _is_confirmation_question(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in _CONFIRMATION_KWS)

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
        self.bug_func_sources_list = data.get("bug_func_sources_list", [])
        self.original_bug_func_sources_list = data.get("original_bug_func_sources_list", [])
        self.function_name = data.get("function_name", "")
        self.nesting_level = data.get("nesting_level", 3)
        self.refactoring_enabled = data.get("refactoring_enabled", False)
        self.debug_mode = data.get("debug_mode", False)
    
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
    
    def challenge_info(self) -> dict:
        """Return challenge metadata for the hint system."""
        return {
            "function_name":                  self.function_name,
            "bug_func_name":                  self.bug_func_name,
            "target_file":                    self.target_file,
            "nesting_level":                  self.nesting_level,
            "refactoring_enabled":            self.refactoring_enabled,
            "debug_mode":                     self.debug_mode,
            "bug_func_names":                 self.bug_func_names,
            "bug_func_sources_list":          self.bug_func_sources_list,
            "original_bug_func_sources_list": self.original_bug_func_sources_list,
            "original_code":                  self.original_code,
        }
    
    def write_target(self, code: str) -> None:
        """Write code to the target file."""
        self.target_path.write_text(code, encoding="utf-8")

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
        "bug_func_sources_list": result.get("bug_func_sources_list", []),
        "original_bug_func_sources_list": result.get("original_bug_func_sources_list", []),
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
            gr.Markdown("""
            **Recommended repositories:**
            - `https://github.com/mahmoud/boltons` (utilities library - works great!)
            - `https://github.com/psf/requests` (HTTP library)
            - `https://github.com/pallets/flask` (web framework)
            """)
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
                    with gr.Row():
                        run_tests_btn = gr.Button("▶️ Run Tests", variant="secondary")
                        show_diff_btn = gr.Button("📊 Show Changes", variant="secondary")
                    test_output_box = gr.HTML(label="Test Results", visible=False)
                    diff_output_box = gr.HTML(label="Code Changes", visible=False)
                
                # Sub-tab: Chat/Hints
                with gr.Tab("💬 Chat", id=2):
                    hint_status_md = gr.Markdown(_hint_md(0, 0))
                    chatbot = gr.Chatbot(label="AI Assistant", height=400)
                    msg_input = gr.Textbox(label="Ask for help", placeholder="Type your question...", lines=2)
                    send_btn = gr.Button("Send 💬", variant="primary")
            
            submit_btn = gr.Button("Submit ➡️", variant="primary", size="lg")
        
        # Hidden state variables for hints and scoring
        hints_used_state = gr.State(0)
        hint_log_state = gr.State([])
        confirmation_pending_state = gr.State(False)
        submission_count_state = gr.State(0)
        
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
    
    def on_start(url, bugs, nesting, refactoring, debug):
        logger.info(f"Starting: {url}, bugs={bugs}, nesting={nesting}, refactoring={refactoring}, debug={debug}")
        yield gr.Tabs(selected=1), "⏳ Creating challenge...", "", "", ""
        
        try:
            workspace = _run_pipeline(
                url.strip(), 
                nesting_level=int(nesting), 
                num_bugs=int(bugs),
                refactoring_enabled=refactoring,
                debug_mode=debug
            )
            cs = ChallengeState(workspace)
            code = cs.read_target()
            readme = cs.readme()
            yield gr.Tabs(selected=2), f"✅ Ready! File: {cs.target_file}", readme, code, workspace
        except Exception as exc:
            logger.error(f"Pipeline failed: {exc}", exc_info=True)
            error_msg = str(exc)
            
            # Provide helpful error messages
            if "not found in source" in error_msg:
                error_msg = f"""❌ **Function not found in repository**
                
The system couldn't find a suitable function to create a challenge.

**Possible solutions:**
1. Try a different repository (one with Python code)
2. Lower the **Nesting Level** slider (try 1 or 2)
3. Use a well-known repo like: `https://github.com/mahmoud/boltons`

**Technical details:** {exc}"""
            elif "git" in error_msg.lower() or "clone" in error_msg.lower():
                error_msg = f"""❌ **Repository access failed**

Could not clone the repository.

**Check:**
- URL is correct and public
- Repository contains Python code

**Error:** {exc}"""
            else:
                error_msg = f"❌ **Error creating challenge:**\n\n{exc}"
            
            yield gr.Tabs(selected=1), error_msg, "", "", ""
    
    def on_submit(workspace, code, hints_used, submit_count):
        logger.info(f"Submit clicked (hints={hints_used}, attempt={submit_count+1})")
        
        # Move to results tab immediately
        yield gr.Tabs(selected=3), "<p style='text-align:center;padding:40px;'>⏳ Running tests...</p>", "", submit_count
        
        try:
            if not workspace:
                yield gr.Tabs(selected=3), "❌ No challenge loaded", "", submit_count
                return
            
            cs = ChallengeState(workspace)
            
            # Save the current code first
            cs.write_target(code)
            
            result = evaluate_submission(
                workspace_path=workspace,
                student_code=code,
                original_code=cs.original_code,
                bug_func_name=cs.bug_func_name,
                hints_used=hints_used,
                sabotaged_code=cs.sabotaged_code,
                target_file=str(cs.target_path),
                bug_func_names=cs.bug_func_names,
            )
            
            # Apply hint penalty
            penalty = PENALTY_TABLE[min(hints_used, len(PENALTY_TABLE) - 1)]
            base_score = result.get("total_score", 0)
            final_score = max(0, base_score - penalty)
            passed = result.get("passed", 0)
            total = result.get("total_tests", 0)
            
            score_html_content = f"""
            <div style='padding:30px;background:#e8f5e9;border-radius:10px;text-align:center;'>
                <h1 style='color:green;margin:0;'>Final Score: {final_score}/100</h1>
                <p style='font-size:1.2em;margin-top:10px;'>✅ {passed}/{total} tests passed</p>
                <p style='margin-top:10px;'>Base Score: {base_score} | Hint Penalty: -{penalty} | Hints Used: {hints_used}</p>
            </div>
            """
            
            tests_output = result.get("test_output", "No test output")
            tests_html_content = f"<pre style='background:#f5f5f5;padding:20px;border-radius:5px;'>{tests_output}</pre>"
            
            yield gr.Tabs(selected=3), score_html_content, tests_html_content, submit_count + 1
            
        except Exception as exc:
            logger.error(f"Submission failed: {exc}", exc_info=True)
            yield gr.Tabs(selected=3), f"❌ Error: {exc}", "", submit_count
    
    # ── Run Tests Handler ─────────────────────────────────────────────────────────
    
    def on_run_tests(code, workspace_path):
        if not workspace_path:
            return gr.HTML("<p style='color:red;'>No challenge loaded</p>", visible=True)
        
        try:
            # Save current code
            cs = ChallengeState(workspace_path)
            cs.write_target(code)
            
            # Run evaluation to get test results
            result = evaluate_submission(
                workspace_path=workspace_path,
                student_code=code,
                original_code=cs.original_code,
                bug_func_name=cs.bug_func_name,
                hints_used=0,
                sabotaged_code=cs.sabotaged_code,
                target_file=str(cs.target_path),
                bug_func_names=cs.bug_func_names,
            )
            
            test_output = result.get("test_output", "No test output")
            passed = result.get("passed", 0)
            total = result.get("total_tests", 0)
            
            # Format output with colors
            html = f"""<div style='background:#1e1e1e;color:#d4d4d4;padding:15px;border-radius:8px;'>
                <h3 style='color:#3b82f6;margin-top:0;'>✅ {passed}/{total} tests passed</h3>
                <pre style='margin:0;white-space:pre-wrap;'>{test_output}</pre>
            </div>"""
            return gr.HTML(html, visible=True)
        except Exception as exc:
            logger.error(f"Run tests failed: {exc}", exc_info=True)
            return gr.HTML(f"<p style='color:red;'>Error: {exc}</p>", visible=True)
    
    # ── Show Diff Handler ─────────────────────────────────────────────────────────
    
    def on_show_diff(code, workspace_path):
        if not workspace_path:
            return gr.HTML("<p style='color:red;'>No challenge loaded</p>", visible=True)
        
        try:
            import difflib
            cs = ChallengeState(workspace_path)
            original = cs.sabotaged_code
            current = code
            
            # Generate unified diff
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                current.splitlines(keepends=True),
                fromfile='Original (with bugs)',
                tofile='Your changes',
                lineterm=''
            )
            diff_text = ''.join(diff)
            
            if not diff_text:
                html = "<p style='color:#22c55e;'>No changes yet</p>"
            else:
                # Colorize diff
                lines = []
                for line in diff_text.split('\n'):
                    if line.startswith('+') and not line.startswith('+++'):
                        lines.append(f'<span style="color:#22c55e;font-weight:bold;">{line}</span>')
                    elif line.startswith('-') and not line.startswith('---'):
                        lines.append(f'<span style="color:#ef4444;font-weight:bold;">{line}</span>')
                    elif line.startswith('@@'):
                        lines.append(f'<span style="color:#3b82f6;font-weight:bold;">{line}</span>')
                    else:
                        lines.append(f'<span>{line}</span>')
                html = f"<pre style='background:#1e1e1e;padding:15px;border-radius:8px;overflow-y:auto;max-height:400px;'>{chr(10).join(lines)}</pre>"
            
            return gr.HTML(html, visible=True)
        except Exception as exc:
            return gr.HTML(f"<p style='color:red;'>Error: {exc}</p>", visible=True)
    
    # ── Chat Handler ──────────────────────────────────────────────────────────────
    
    def on_send(message, history, hints_used, submit_count, workspace_path, hint_log, confirmation_pending):
        if not message.strip():
            penalty = PENALTY_TABLE[min(hints_used, len(PENALTY_TABLE) - 1)]
            return history, "", hints_used, _hint_md(hints_used, penalty), hint_log, confirmation_pending
        
        if not workspace_path:
            history = list(history or [])
            history.append([message, "No challenge loaded yet."])
            return history, "", hints_used, _hint_md(hints_used, 0), hint_log, False
        
        cs = ChallengeState(workspace_path)
        result = get_hint(
            user_message=message,
            history=history,
            hints_used=hints_used,
            submission_attempts=submit_count,
            challenge_info=cs.challenge_info(),
        )
        
        # Check if hint was given
        accepted_pending = confirmation_pending and not _is_decline(message)
        gave_hint = result["gave_hint"] or accepted_pending
        new_confirmation_pending = not gave_hint and _is_confirmation_question(result["response"])
        
        # Gradio Chatbot format: list of [user_msg, bot_msg] pairs
        history = list(history or [])
        history.append([message, result["response"]])
        new_hints = hints_used + (1 if gave_hint else 0)
        penalty = PENALTY_TABLE[min(new_hints, len(PENALTY_TABLE) - 1)]
        new_log = list(hint_log or [])
        if gave_hint:
            new_log.append({"summary": result.get("hint_summary", ""), "response": result["response"]})
        
        return history, "", new_hints, _hint_md(new_hints, penalty), new_log, new_confirmation_pending
    
    # ── Wire events ───────────────────────────────────────────────────────────────
    
    login_btn.click(on_login, inputs=[name_input, api_input], outputs=[tabs])
    start_btn.click(on_start, inputs=[url_input, num_bugs, nesting_slider, refactoring_check, debug_check], outputs=[tabs, status_md, readme_md, code_box, workspace_state])
    
    # Code Editor Tools
    run_tests_btn.click(on_run_tests, inputs=[code_box, workspace_state], outputs=[test_output_box])
    show_diff_btn.click(on_show_diff, inputs=[code_box, workspace_state], outputs=[diff_output_box])
    
    # Chat
    send_btn.click(
        on_send,
        inputs=[msg_input, chatbot, hints_used_state, submission_count_state, workspace_state, hint_log_state, confirmation_pending_state],
        outputs=[chatbot, msg_input, hints_used_state, hint_status_md, hint_log_state, confirmation_pending_state]
    )
    msg_input.submit(
        on_send,
        inputs=[msg_input, chatbot, hints_used_state, submission_count_state, workspace_state, hint_log_state, confirmation_pending_state],
        outputs=[chatbot, msg_input, hints_used_state, hint_status_md, hint_log_state, confirmation_pending_state]
    )
    
    # Submit
    submit_btn.click(on_submit, inputs=[workspace_state, code_box, hints_used_state, submission_count_state], outputs=[tabs, score_html, tests_html, submission_count_state])

demo.queue()

if __name__ == "__main__":
    demo.launch()
