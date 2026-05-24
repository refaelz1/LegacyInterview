"""Real Legacy Code Challenge - Working version with Columns"""
import gradio as gr
import os
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── ChallengeState (copied from student_interface.py) ────────────────────────

class ChallengeState:
    """Loads and exposes data from challenge_state.json."""

    def __init__(self, workspace_path: str) -> None:
        self.workspace = Path(workspace_path)
        state_file = self.workspace / "challenge_state.json"
        if not state_file.exists():
            raise FileNotFoundError(f"challenge_state.json not found in {workspace_path}")
        with open(state_file, encoding="utf-8") as f:
            data = json.load(f)

        self.github_url = data.get("github_url", "")
        raw_target = data.get("target_file", "")
        try:
            self.target_file = Path(raw_target).resolve().relative_to(self.workspace.resolve()).as_posix()
        except (ValueError, OSError):
            self.target_file = Path(raw_target).as_posix()
        self.original_code = data.get("original_code", "")
        self.sabotaged_code = data.get("sabotaged_code", "")
        self.function_name = data.get("function_name", "")
        self.bug_func_name = data.get("bug_func_name", "")
        
        # sabotaged_files
        snapshot_dir = self.workspace / ".metadata"
        snap_files = {}
        if snapshot_dir.exists():
            target_rel_from_json = data.get("target_file", "")
            if target_rel_from_json:
                try:
                    target_abs = Path(target_rel_from_json).resolve()
                    target_rel = target_abs.relative_to(self.workspace.resolve()).as_posix()
                except (ValueError, OSError):
                    target_rel = Path(target_rel_from_json).as_posix()
                
                expected_snapshot_name = target_rel.replace("/", "__")
                snapshot_path = snapshot_dir / expected_snapshot_name
                
                if snapshot_path.exists():
                    try:
                        snap_files[target_rel] = snapshot_path.read_text(encoding="utf-8")
                    except Exception:
                        pass

        if snap_files:
            self.sabotaged_files = snap_files
        else:
            stored = data.get("sabotaged_files", {})
            if not stored and self.sabotaged_code:
                try:
                    rel = Path(self.target_file).resolve().relative_to(self.workspace.resolve()).as_posix()
                except ValueError:
                    rel = Path(self.target_file).name
                stored = {rel: self.sabotaged_code}
            self.sabotaged_files = stored

    @property
    def target_path(self) -> Path:
        return self.workspace / self.target_file

    def read_target(self) -> str:
        if self.target_path.exists():
            return self.target_path.read_text(encoding="utf-8")
        return self.sabotaged_code

    def write_target(self, code: str) -> None:
        self.target_path.write_text(code, encoding="utf-8")

    def list_py_files(self) -> list[str]:
        files = sorted(self.workspace.rglob("*.py"))
        return [
            f.relative_to(self.workspace).as_posix() for f in files
            if ".metadata" not in f.parts
        ]

    def readme(self) -> str:
        readme_path = self.workspace / "STUDENT_README.md"
        if readme_path.exists():
            return readme_path.read_text(encoding="utf-8")
        return "# Challenge\n\nREADME not found."

# ── Pipeline function (copied from student_interface.py) ─────────────────────

def _run_pipeline(github_url: str, nesting_level: int, num_bugs: int, 
                  refactoring_enabled: bool = False, debug_mode: bool = False) -> str:
    """Invoke the architect pipeline and return the workspace path."""
    from architect.graph import build_graph

    graph = build_graph()
    result = graph.invoke({
        "github_url":          github_url,
        "nesting_level":       nesting_level,
        "refactoring_enabled": refactoring_enabled,
        "debug_mode":          debug_mode,
        "num_bugs":            num_bugs,
        "clone_path":          "",
        "target_file":         "",
        "original_code":       "",
        "sabotaged_code":      "",
        "function_name":       "",
        "test_args":           "",
        "expected_output":     "",
        "actual_output":       "",
        "bug_description":     "",
        "detailed_explanation": "",
        "challenge_summary":   "",
        "test_cases":          [],
        "public_tests":        [],
        "secret_tests":        [],
        "candidate_files":     [],
        "bug_func_name":       "",
        "bug_func_source":     "",
        "call_chain":          {},
    })

    workspace_path = result["clone_path"]
    target_file_rel = result.get("target_file", "")
    actual_sabotaged_code = result.get("sabotaged_code", "")
    
    workspace_path_obj = Path(workspace_path).resolve()
    if target_file_rel:
        target_path = Path(workspace_path) / target_file_rel
        if target_path.exists():
            actual_sabotaged_code = target_path.read_text(encoding="utf-8")

    sabotaged_files: dict[str, str] = {}
    if target_file_rel and actual_sabotaged_code:
        try:
            rel_posix = Path(target_file_rel).resolve().relative_to(workspace_path_obj).as_posix()
        except (ValueError, OSError):
            rel_posix = Path(target_file_rel).as_posix()
        sabotaged_files[rel_posix] = actual_sabotaged_code

    # Persist challenge_state.json
    challenge_state = {
        "github_url":          github_url,
        "workspace_path":      workspace_path,
        "target_file":         target_file_rel,
        "original_code":       result.get("original_code", ""),
        "sabotaged_code":      actual_sabotaged_code,
        "sabotaged_files":     sabotaged_files,
        "function_name":       result.get("function_name", ""),
        "bug_func_name":       result.get("bug_func_name", ""),
        "test_cases":          result.get("test_cases", []),
        "public_tests":        result.get("public_tests", []),
        "secret_tests":        result.get("secret_tests", []),
        "nesting_level":       nesting_level,
        "refactoring_enabled": refactoring_enabled,
        "debug_mode":          debug_mode,
        "bug_description":     result.get("bug_description", ""),
    }
    state_path = Path(workspace_path) / "challenge_state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(challenge_state, f, indent=2, ensure_ascii=False)

    return workspace_path

with gr.Blocks(title="Legacy Code Challenge", theme=gr.themes.Soft()) as demo:
    
    # Page 1: Login
    with gr.Column(visible=True) as login_page:
        gr.Markdown("# 🔐 כניסה למערכת")
        gr.Markdown("הזן את הפרטים שלך כדי להתחיל")
        
        name_input = gr.Textbox(label="שם מלא", placeholder="הזן את שמך...", rtl=True)
        api_input = gr.Textbox(label="OpenAI API Key", placeholder="sk-proj-...", type="password")
        login_btn = gr.Button("התחבר ➡️", variant="primary", size="lg")
    
    # Page 2: Setup
    with gr.Column(visible=False) as setup_page:
        gr.Markdown("# ⚙️ הגדרת אתגר")
        gr.Markdown("בחר repository ופרמטרים")
        
        url_input = gr.Textbox(
            label="GitHub Repository URL",
            value="https://github.com/mahmoud/boltons"
        )
        num_bugs = gr.Slider(1, 5, value=3, step=1, label="מספר באגים")
        num_tests = gr.Slider(5, 30, value=15, step=5, label="מספר טסטים")
        
        start_btn = gr.Button("התחל אתגר ➡️", variant="primary", size="lg")
        status_box = gr.Textbox(label="סטטוס", interactive=False, lines=3)
    
    # Page 3: Challenge
    with gr.Column(visible=False) as challenge_page:
        gr.Markdown("# 💻 תקן את הקוד")
        gr.Markdown("הקוד להלן מכיל באגים. תקן אותם ולחץ על 'שלח'")
        
        code_display = gr.Textbox(
            label="קוד עם באגים",
            lines=20,
            value="# הקוד יוצג כאן לאחר יצירת האתגר\ndef hello():\n    print('Hello World')\n\nhello()",
            max_lines=30
        )
        
        submit_btn = gr.Button("שלח פתרון ➡️", variant="primary", size="lg")
    
    # Page 4: Results
    with gr.Column(visible=False) as results_page:
        gr.Markdown("# 🎯 תוצאות הערכה")
        
        score_html = gr.HTML("<h2>הציון שלך יופיע כאן</h2>")
        diff_html = gr.HTML("<h3>שינויים</h3>")
        tests_html = gr.HTML("<h3>טסטים</h3>")
        hints_html = gr.HTML("<h3>רמזים</h3>")
    
    # Event handlers
    def on_login(name, api_key):
        if not name or not api_key:
            return gr.update(visible=True), gr.update(visible=False)
        # Save API key to environment
        os.environ["OPENAI_API_KEY"] = api_key
        logger.info(f"User logged in: {name}")
        return gr.update(visible=False), gr.update(visible=True)
    
    def on_start(url, bugs, tests):
        logger.info(f"Starting challenge: {url}, bugs={bugs}, tests={tests}")
        
        # Show loading
        yield (
            "⏳ Cloning repository and generating challenge... this may take 1-2 minutes.",
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update()  # code_display - no change
        )
        
        try:
            # Run the REAL pipeline!
            workspace_path = _run_pipeline(
                url.strip(),
                nesting_level=2,  # default
                num_bugs=int(bugs),
                refactoring_level=0,  # default
                debug_mode=False
            )
            
            logger.info(f"Pipeline complete! Workspace: {workspace_path}")
            
            # Load challenge state
            cs = ChallengeState(workspace_path)
            code = cs.read_target()
            
            # Move to challenge page
            yield (
                f"✅ Challenge ready! File: {cs.target_file}",
                gr.update(visible=False),
                gr.update(visible=True),
                code  # Update code_display
            )
            
        except Exception as exc:
            logger.error(f"Pipeline failed: {exc}", exc_info=True)
            yield (
                f"❌ Error: {exc}",
                gr.update(visible=True),
                gr.update(visible=False),
                ""
            )
    
    def on_submit():
        # Immediate response - no processing
        yield (
            gr.update(visible=False),  # challenge_page
            gr.update(visible=True),   # results_page
            "<div style='padding:20px;background:#e8f5e9;border-radius:10px;'><h2 style='color:green;'>✅ ציון: 85/100</h2></div>",
            "<p>Diff יופיע כאן...</p>",
            "<p>Tests יופיעו כאן...</p>",
            "<p>Hints יופיעו כאן...</p>"
        )
    
    # Wire events
    login_btn.click(
        fn=on_login,
        inputs=[name_input, api_input],
        outputs=[login_page, setup_page]
    )
    
    start_btn.click(
        fn=on_start,
        inputs=[url_input, num_bugs, num_tests],
        outputs=[status_box, setup_page, challenge_page, code_display]
    )
    
    submit_btn.click(
        fn=on_submit,
        inputs=[],
        outputs=[challenge_page, results_page, score_html, diff_html, tests_html, hints_html]
    )

demo.queue()

if __name__ == "__main__":
    demo.launch(share=False, inbrowser=True)
