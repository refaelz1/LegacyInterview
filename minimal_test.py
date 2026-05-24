"""Minimal test - Using Tabs instead of Columns"""
import gradio as gr

with gr.Blocks(title="Test Navigation") as demo:
    with gr.Tabs() as tabs:
        with gr.Tab("עמוד 1", id=0):
            gr.Markdown("# 🏠 עמוד 1 - התחלה")
            gr.HTML("<p style='font-size:20px;'>זהו העמוד הראשון</p>")
            btn1 = gr.Button("➡️ עמוד 2", variant="primary", size="lg")
        
        with gr.Tab("עמוד 2", id=1):
            gr.Markdown("# 📝 עמוד 2")
            gr.HTML("<p style='color:blue;font-size:18px;'>✅ מעבר 1 הצליח!</p>")
            btn2 = gr.Button("➡️ עמוד 3", variant="primary", size="lg")
        
        with gr.Tab("עמוד 3", id=2):
            gr.Markdown("# 💻 עמוד 3")
            gr.HTML("<p style='color:green;font-size:18px;'>✅✅ מעבר 2 הצליח!</p>")
            btn3 = gr.Button("➡️ עמוד 4", variant="primary", size="lg")
        
        with gr.Tab("עמוד 4", id=3):
            gr.Markdown("# ⚙️ עמוד 4")
            gr.HTML("<p style='color:orange;font-size:18px;'>✅✅✅ מעבר 3 הצליח!</p>")
            btn4 = gr.Button("➡️ עמוד 5 (תוצאות)", variant="primary", size="lg")
        
        with gr.Tab("תוצאות", id=4):
            gr.Markdown("# 🎯 עמוד 5 - תוצאות")
            gr.HTML("<h2 style='color:green;text-align:center;'>✅✅✅✅ כל המעברים עבדו!</h2>")
            gr.HTML("""
                <div style='padding:20px;background:#e8f5e9;border-radius:10px;margin-top:20px;'>
                    <h3>ציון: 100/100</h3>
                    <p>✅ כל 5 העמודים עובדים מצוין!</p>
                </div>
            """)
    
    btn1.click(fn=lambda: gr.Tabs(selected=1), inputs=[], outputs=[tabs])
    btn2.click(fn=lambda: gr.Tabs(selected=2), inputs=[], outputs=[tabs])
    btn3.click(fn=lambda: gr.Tabs(selected=3), inputs=[], outputs=[tabs])
    btn4.click(fn=lambda: gr.Tabs(selected=4), inputs=[], outputs=[tabs])

demo.queue()

if __name__ == "__main__":
    demo.launch(share=False, inbrowser=True)
