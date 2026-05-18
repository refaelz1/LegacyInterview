"""
Patch to add login page to student_interface.py
This adds user registration with API key input before the main interface.
"""

# Add this function at the top of student_interface.py, before create_full_interface():

def validate_openai_key(api_key: str) -> tuple[bool, str]:
    """Validate that an OpenAI API key is properly formatted and works."""
    import os
    if not api_key or not api_key.startswith("sk-"):
        return False, "Invalid API key format. Must start with 'sk-'"
    
    # Try a simple API call to validate
    try:
        os.environ["OPENAI_API_KEY"] = api_key
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o", temperature=0, request_timeout=5, max_tokens=5)
        llm.invoke("test")
        return True, "✅ API key validated successfully!"
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Incorrect API key" in error_msg:
            return False, "❌ Invalid API key. Please check your key."
        elif "quota" in error_msg.lower():
            return False, "⚠️ API key valid but no quota remaining."
        else:
            # Key is probably valid, just another error
            return True, f"⚠️ API key accepted (error: {error_msg[:50]})"


# Then modify create_full_interface() to add login page:
# Add after line "with gr.Blocks..." and before "# Shared state":

        # ════════════════════════════════════════════════════════════════════
        # PAGE 0 — Login/Registration  
        # ════════════════════════════════════════════════════════════════════
        user_api_key_state = gr.State("")
        user_name_state = gr.State("")
        
        with gr.Column(visible=True, elem_classes=["setup-card"]) as login_page:
            gr.Markdown(
                "# 🔐 Welcome to Legacy Code Challenge\n"
                "### Please enter your details to continue"
            )
            
            login_name = gr.Textbox(
                label="Your Name",
                placeholder="e.g. Alice Smith",
                info="This will appear in your challenge session",
            )
            
            login_api_key = gr.Textbox(
                label="OpenAI API Key",
                placeholder="sk-proj-...",
                type="password",
                info="Your API key will be used only for this session",
            )
            
            gr.Markdown(
                "💡 **Don't have an API key?** Get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)\n\n"
                "⚠️ **Note:** Running challenges will consume API credits from your OpenAI account"
            )
            
            login_btn = gr.Button("🚀 Continue to Challenge Setup", variant="primary", size="lg")
            login_status = gr.Markdown("")


# Add this callback at the bottom, before "return demo":

        def on_login(name, api_key):
            if not name.strip():
                return (
                    gr.update(visible=True),
                    gr.update(visible=False),
                    "❌ Please enter your name",
                    "", ""
                )
            
            valid, msg = validate_openai_key(api_key)
            if not valid:
                return (
                    gr.update(visible=True),
                    gr.update(visible=False),
                    msg,
                    "", ""
                )
            
            # Success - hide login, show setup
            import os
            os.environ["OPENAI_API_KEY"] = api_key
            return (
                gr.update(visible=False),  # hide login
                gr.update(visible=True),   # show setup
                msg,
                api_key,  # save to state
                name.strip()  # save name to state
            )
        
        login_btn.click(
            on_login,
            inputs=[login_name, login_api_key],
            outputs=[login_page, setup_page, login_status, user_api_key_state, user_name_state],
        )


# Modify on_start() to use user_name_state instead of name_box:
# Change the first line from:
#   def on_start(name, url, nesting_lvl, num_bugs, refactoring, debug, timer_mins):
# To:
#   def on_start(saved_name, url, nesting_lvl, num_bugs, refactoring, debug, timer_mins):
# And use saved_name instead of name throughout

# Update start_btn.click():
# Change inputs from:
#   inputs=[name_box, url_box, ...]
# To:
#   inputs=[user_name_state, url_box, ...]
