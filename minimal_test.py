"""Minimal test - 3 pages with buttons to switch between them"""
import gradio as gr

# Page 1
with gr.Blocks() as demo:
    with gr.Column(visible=True) as page1:
        gr.Markdown("# עמוד 1 - התחלה")
        gr.Markdown("זהו העמוד הראשון")
        btn1 = gr.Button("🔹 לחץ כאן למעבר לעמוד 2", size="lg")
    
    with gr.Column(visible=False) as page2:
        gr.Markdown("# עמוד 2 - אמצע")
        gr.HTML("<h2 style='color:blue;'>✅ המעבר הראשון עבד!</h2>")
        btn2 = gr.Button("🔹 לחץ כאן למעבר לעמוד 3", size="lg")
    
    with gr.Column(visible=False) as page3:
        gr.Markdown("# עמוד 3 - סוף")
        gr.HTML("<h2 style='color:green;'>✅✅ שני המעברים עבדו בהצלחה!</h2>")
        gr.Markdown("**כל המעברים עובדים מצוין** 🎉")
    
    def switch_to_page2():
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
    
    def switch_to_page3():
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
    
    btn1.click(
        fn=switch_to_page2,
        inputs=[],
        outputs=[page1, page2, page3]
    )
    
    btn2.click(
        fn=switch_to_page3,
        inputs=[],
        outputs=[page1, page2, page3]
    )

if __name__ == "__main__":
    demo.launch(share=False, inbrowser=True)
