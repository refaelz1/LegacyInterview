"""Real Legacy Code Challenge - Working version with Columns"""
import gradio as gr
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the real pipeline
from architect.challenge_deployer import run_pipeline as _run_pipeline
from challenge import ChallengeState

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
