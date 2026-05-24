"""Using Columns but only 2 at a time - linear flow"""
import gradio as gr

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
    
    # Event handlers - only 2 outputs each time!
    def on_login(name, api_key):
        if not name or not api_key:
            return gr.update(visible=True), gr.update(visible=False)
        return gr.update(visible=False), gr.update(visible=True)
    
    def on_start(url, bugs, tests):
        status = f"מתחיל...\n{url}\nבאגים: {bugs}, טסטים: {tests}"
        return status, gr.update(visible=False), gr.update(visible=True)
    
    def on_submit():
        results = """
        <div style='padding:20px;background:#e8f5e9;border-radius:10px;'>
            <h2 style='color:green;'>✅ ציון: 85/100</h2>
        </div>
        """
        return (
            gr.update(visible=False),  # challenge_page
            gr.update(visible=True),   # results_page
            results,                   # score_html
            "<p>Diff...</p>",         # diff_html
            "<p>Tests...</p>",        # tests_html
            "<p>Hints...</p>"         # hints_html
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
        outputs=[status_box, setup_page, challenge_page]
    )
    
    submit_btn.click(
        fn=on_submit,
        inputs=[],
        outputs=[challenge_page, results_page, score_html, diff_html, tests_html, hints_html]
    )

demo.queue()

if __name__ == "__main__":
    demo.launch(share=False, inbrowser=True)
