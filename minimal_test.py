"""Minimal test - 4 pages simulating the full flow"""
import gradio as gr

with gr.Blocks(title="Legacy Code Challenge - Test") as demo:
    # Page 1: Login
    with gr.Column(visible=True) as page1:
        gr.Markdown("# 🔐 עמוד התחברות")
        gr.Markdown("הזן שם וAPI key")
        name_input = gr.Textbox(label="שם", value="Test User")
        api_input = gr.Textbox(label="API Key", type="password", value="test-key")
        btn1 = gr.Button("התחבר ➡️", variant="primary", size="lg")
    
    # Page 2: Setup Challenge
    with gr.Column(visible=False) as page2:
        gr.Markdown("# ⚙️ הגדרת אתגר")
        gr.Markdown("בחר repository ורמת קושי")
        url_input = gr.Textbox(label="GitHub URL", value="https://github.com/test/repo")
        difficulty = gr.Slider(1, 5, value=3, label="קושי")
        btn2 = gr.Button("התחל אתגר ➡️", variant="primary", size="lg")
    
    # Page 3: Challenge (coding)
    with gr.Column(visible=False) as page3:
        gr.Markdown("# 💻 עמוד האתגר")
        gr.Markdown("כאן תקבל את הקוד המקולקל")
        gr.Markdown("```python\n# Your buggy code here\nprint('Hello')\n```")
        gr.Textbox(label="ערוך את הקוד כאן", lines=10, value="# Fix the bugs here\nprint('Hello')")
        btn3 = gr.Button("שלח ➡️", variant="primary", size="lg")
    
    # Page 4: Results
    with gr.Column(visible=False) as page4:
        gr.Markdown("# 🎯 תוצאות")
        gr.HTML("<h2 style='color:green;text-align:center;'>✅ עמוד התוצאות עובד!</h2>")
        results_html = gr.HTML("""
            <div style='padding:20px;background:#f0f0f0;border-radius:10px;'>
                <h3>ציון: 85/100</h3>
                <p>✅ 8 מתוך 10 טסטים עברו</p>
                <p>📝 שינויים: 5 שורות</p>
                <p>💡 רמזים: 2</p>
            </div>
        """)
    
    def switch_to_setup():
        return (
            gr.update(visible=False),  # page1
            gr.update(visible=True),   # page2
            gr.update(visible=False),  # page3
            gr.update(visible=False),  # page4
        )
    
    def switch_to_challenge():
        return (
            gr.update(visible=False),  # page1
            gr.update(visible=False),  # page2
            gr.update(visible=True),   # page3
            gr.update(visible=False),  # page4
        )
    
    def switch_to_results():
        return (
            gr.update(visible=False),  # page1
            gr.update(visible=False),  # page2
            gr.update(visible=False),  # page3
            gr.update(visible=True),   # page4
        )
    
    btn1.click(fn=switch_to_setup, inputs=[], outputs=[page1, page2, page3, page4])
    btn2.click(fn=switch_to_challenge, inputs=[], outputs=[page1, page2, page3, page4])
    btn3.click(fn=switch_to_results, inputs=[], outputs=[page1, page2, page3, page4])

# Enable queue for server compatibility
demo.queue()

if __name__ == "__main__":
    demo.launch(share=False, inbrowser=True)
