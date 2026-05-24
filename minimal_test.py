"""Minimal test - 5 simple pages"""
import gradio as gr

with gr.Blocks(title="Test 5 Pages") as demo:
    # Page 1
    with gr.Column(visible=True) as page1:
        gr.Markdown("# עמוד 1 - התחלה")
        gr.HTML("<p style='font-size:20px;'>זהו העמוד הראשון</p>")
        btn1 = gr.Button("➡️ עמוד 2", variant="primary", size="lg")
    
    # Page 2
    with gr.Column(visible=False) as page2:
        gr.Markdown("# עמוד 2")
        gr.HTML("<p style='color:blue;'>✅ מעבר 1 הצליח!</p>")
        btn2 = gr.Button("➡️ עמוד 3", variant="primary", size="lg")
    
    # Page 3
    with gr.Column(visible=False) as page3:
        gr.Markdown("# עמוד 3")
        gr.HTML("<p style='color:green;'>✅✅ מעבר 2 הצליח!</p>")
        btn3 = gr.Button("➡️ עמוד 4", variant="primary", size="lg")
    
    # Page 4
    with gr.Column(visible=False) as page4:
        gr.Markdown("# עמוד 4")
        gr.HTML("<p style='color:orange;'>✅✅✅ מעבר 3 הצליח!</p>")
        btn4 = gr.Button("➡️ עמוד 5 (תוצאות)", variant="primary", size="lg")
    
    # Page 5 - Results
    with gr.Column(visible=False) as page5:
        gr.Markdown("# 🎯 עמוד 5 - תוצאות")
        gr.HTML("<h2 style='color:green;text-align:center;'>✅✅✅✅ כל המעברים עבדו!</h2>")
        gr.HTML("""
            <div style='padding:20px;background:#e8f5e9;border-radius:10px;margin-top:20px;'>
                <h3>ציון: 100/100</h3>
                <p>✅ כל 5 העמודים עובדים מצוין!</p>
            </div>
        """)
    
    def goto_page2():
        return (gr.update(visible=False), gr.update(visible=True), 
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False))
    
    def goto_page3():
        return (gr.update(visible=False), gr.update(visible=False), 
                gr.update(visible=True), gr.update(visible=False), gr.update(visible=False))
    
    def goto_page4():
        return (gr.update(visible=False), gr.update(visible=False), 
                gr.update(visible=False), gr.update(visible=True), gr.update(visible=False))
    
    def goto_page5():
        return (gr.update(visible=False), gr.update(visible=False), 
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=True))
    
    btn1.click(fn=goto_page2, inputs=[], outputs=[page1, page2, page3, page4, page5])
    btn2.click(fn=goto_page3, inputs=[], outputs=[page1, page2, page3, page4, page5])
    btn3.click(fn=goto_page4, inputs=[], outputs=[page1, page2, page3, page4, page5])
    btn4.click(fn=goto_page5, inputs=[], outputs=[page1, page2, page3, page4, page5])

demo.queue()

if __name__ == "__main__":
    demo.launch(share=False, inbrowser=True)
