"""Real interface with Tabs - Login → Setup → Challenge → Results"""
import gradio as gr

with gr.Blocks(title="Legacy Code Challenge", theme=gr.themes.Soft()) as demo:
    with gr.Tabs() as tabs:
        # Tab 0: Login
        with gr.Tab("🔐 התחברות", id=0):
            gr.Markdown("# 🔐 כניסה למערכת")
            gr.Markdown("הזן את הפרטים שלך כדי להתחיל")
            
            name_input = gr.Textbox(
                label="שם מלא",
                placeholder="הזן את שמך...",
                rtl=True
            )
            api_input = gr.Textbox(
                label="OpenAI API Key",
                placeholder="sk-proj-...",
                type="password"
            )
            login_btn = gr.Button("התחבר ➡️", variant="primary", size="lg")
        
        # Tab 1: Setup
        with gr.Tab("⚙️ הגדרות", id=1):
            gr.Markdown("# ⚙️ הגדרת אתגר")
            gr.Markdown("בחר repository ופרמטרים")
            
            url_input = gr.Textbox(
                label="GitHub Repository URL",
                placeholder="https://github.com/user/repo",
                value="https://github.com/mahmoud/boltons"
            )
            num_bugs = gr.Slider(1, 5, value=3, step=1, label="מספר באגים")
            num_tests = gr.Slider(5, 30, value=15, step=5, label="מספר טסטים")
            
            start_btn = gr.Button("התחל אתגר ➡️", variant="primary", size="lg")
            status_box = gr.Textbox(label="סטטוס", interactive=False, lines=3)
        
        # Tab 2: Challenge
        with gr.Tab("💻 האתגר", id=2):
            gr.Markdown("# 💻 תקן את הקוד")
            gr.Markdown("הקוד להלן מכיל באגים. תקן אותם ולחץ על 'שלח'")
            
            code_display = gr.Code(
                label="קוד עם באגים",
                language="python",
                lines=20,
                value="# הקוד יוצג כאן לאחר יצירת האתגר\nprint('Hello World')"
            )
            
            with gr.Row():
                hint_btn = gr.Button("💡 רמז", variant="secondary")
                submit_btn = gr.Button("שלח פתרון ➡️", variant="primary", size="lg")
            
            hint_display = gr.Markdown("💡 לחץ על 'רמז' לקבלת עזרה")
        
        # Tab 3: Results
        with gr.Tab("🎯 תוצאות", id=3):
            gr.Markdown("# 🎯 תוצאות הערכה")
            
            score_html = gr.HTML("<h2>הציון שלך יופיע כאן</h2>")
            diff_html = gr.HTML("<h3>שינויים</h3><p>השינויים שביצעת יופיעו כאן</p>")
            tests_html = gr.HTML("<h3>טסטים</h3><p>תוצאות הטסטים יופיעו כאן</p>")
            hints_html = gr.HTML("<h3>רמזים</h3><p>הרמזים שקיבלת יופיעו כאן</p>")
    
    # Event handlers
    def on_login(name, api_key):
        if not name or not api_key:
            return gr.Tabs(selected=0)
        # Save to state, move to setup
        return gr.Tabs(selected=1)
    
    def on_start(url, bugs, tests):
        # Here we'll call the real pipeline later
        status = f"מתחיל אתגר...\nURL: {url}\nבאגים: {bugs}\nטסטים: {tests}"
        return status, gr.Tabs(selected=2)
    
    def on_submit():
        # Here we'll call the real evaluation later
        results = """
        <div style='padding:20px;background:#e8f5e9;border-radius:10px;'>
            <h2 style='color:green;'>✅ ציון: 85/100</h2>
            <p>8 מתוך 10 טסטים עברו בהצלחה!</p>
        </div>
        """
        return gr.Tabs(selected=3), results, "<p>Diff...</p>", "<p>Tests...</p>", "<p>Hints...</p>"
    
    # Wire up events
    login_btn.click(
        fn=on_login,
        inputs=[name_input, api_input],
        outputs=[tabs]
    )
    
    start_btn.click(
        fn=on_start,
        inputs=[url_input, num_bugs, num_tests],
        outputs=[status_box, tabs]
    )
    
    submit_btn.click(
        fn=on_submit,
        inputs=[],
        outputs=[tabs, score_html, diff_html, tests_html, hints_html]
    )

demo.queue()

if __name__ == "__main__":
    demo.launch(share=False, inbrowser=True)
