# הוספת Login Page + Logout Button

## שלב 1: הוסף פונקציית validation

הוסף את הקוד הזה **בתחילת** `student_interface.py`, אחרי ה-imports:

```python
def validate_openai_key(api_key: str) -> tuple[bool, str]:
    """Validate OpenAI API key by making a test call."""
    import os
    if not api_key or not api_key.startswith("sk-"):
        return False, "❌ Invalid API key format. Must start with 'sk-'"
    
    try:
        os.environ["OPENAI_API_KEY"] = api_key
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o", temperature=0, request_timeout=10, max_tokens=5)
        llm.invoke("test")
        return True, "✅ API key validated!"
    except Exception as e:
        error = str(e)
        if "401" in error or "Incorrect API key" in error:
            return False, "❌ Invalid API key"
        elif "quota" in error.lower():
            return False, "⚠️ API key valid but no quota"
        return True, f"✅ Key accepted"
```

---

## שלב 2: שנה את `create_full_interface()`

**החלף את ההגדרה של הפונקציה:**

```python
def create_full_interface() -> gr.Blocks:
    """
    Returns a Gradio app with login page (if needed) + challenge interface.
    """
    import os
    
    # Auto-detect: יש API key ב-.env?
    has_env_key = bool(os.getenv("OPENAI_API_KEY"))
    
    css = """
    /* ... הCSS הקיים ... */
    
    /* Logout button in corner */
    #logout-btn {
        position: absolute;
        top: 20px;
        right: 20px;
        z-index: 1000;
    }
    """
    
    with gr.Blocks(title="Legacy Code Challenge", css=css) as demo:
        
        # State
        user_api_key_state = gr.State("")
        user_name_state = gr.State("")
        workspace_state = gr.State("")
        hints_used_state = gr.State(0)
        submission_count_state = gr.State(0)
        hint_log_state = gr.State([])
        confirmation_pending_state = gr.State(False)
        timer_trigger = gr.Number(value=0, visible=False)
        
        # Logout button (hidden until logged in)
        with gr.Row():
            gr.HTML("")  # spacer
            logout_btn = gr.Button("🔓 Logout", visible=False, elem_id="logout-btn", size="sm")
        
        # ════════════════════════════════════════════════════════════════════
        # PAGE 0 — Login (hidden if .env exists)
        # ════════════════════════════════════════════════════════════════════
        with gr.Column(visible=not has_env_key, elem_classes=["setup-card"]) as login_page:
            gr.Markdown(
                "# 🔐 Welcome to Legacy Code Challenge\n"
                "### Please enter your details to continue"
            )
            
            login_name = gr.Textbox(
                label="Your Name",
                placeholder="e.g. Alice Smith",
            )
            
            login_api_key = gr.Textbox(
                label="OpenAI API Key",
                placeholder="sk-proj-...",
                type="password",
                info="Get one at platform.openai.com/api-keys",
            )
            
            gr.Markdown(
                "⚠️ **Note:** Your API key is only used for this session and consumes credits from your OpenAI account"
            )
            
            login_btn = gr.Button("🚀 Continue", variant="primary", size="lg")
            login_status = gr.Markdown("")
        
        # ════════════════════════════════════════════════════════════════════
        # PAGE 1 — Setup (visible if .env exists, else hidden)
        # ════════════════════════════════════════════════════════════════════
        with gr.Column(visible=has_env_key, elem_classes=["setup-card"]) as setup_page:
            gr.Markdown(
                "# 🐛 Legacy Code Challenge\n"
                "Fill in the details below, then click **Start Challenge**."
            )
            
            # השאר את כל ה-setup page כמו שהיה...
            name_box = gr.Textbox(...)
            url_box = gr.Textbox(...)
            # ... שאר השדות
```

---

## שלב 3: הוסף callbacks

**הוסף בסוף הפונקציה, לפני `return demo`:**

```python
        # ── Login callback ────────────────────────────────────────────────
        def on_login(name, api_key):
            if not name.strip():
                return (
                    gr.update(),  # login page stays
                    gr.update(),  # setup page hidden
                    gr.update(),  # logout hidden
                    "❌ Please enter your name",
                    "", ""  # states empty
                )
            
            valid, msg = validate_openai_key(api_key)
            if not valid:
                return (
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    msg,
                    "", ""
                )
            
            # Success!
            import os
            os.environ["OPENAI_API_KEY"] = api_key
            return (
                gr.update(visible=False),  # hide login
                gr.update(visible=True),   # show setup
                gr.update(visible=True),   # show logout
                msg,
                api_key,    # save to state
                name.strip()
            )
        
        login_btn.click(
            on_login,
            inputs=[login_name, login_api_key],
            outputs=[login_page, setup_page, logout_btn, login_status, 
                     user_api_key_state, user_name_state],
        )
        
        # ── Logout callback ───────────────────────────────────────────────
        def on_logout():
            import os
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            return (
                gr.update(visible=True),   # show login
                gr.update(visible=False),  # hide setup
                gr.update(visible=False),  # hide challenge
                gr.update(visible=False),  # hide results
                gr.update(visible=False),  # hide logout
                "", "", "", 0, 0, []       # clear states
            )
        
        logout_btn.click(
            on_logout,
            outputs=[login_page, setup_page, challenge_page, results_page, logout_btn,
                     user_api_key_state, user_name_state, workspace_state, 
                     hints_used_state, submission_count_state, hint_log_state],
        )
```

---

## שלב 4: עדכן את on_start

**שנה את השורה הראשונה של `on_start`:**

```python
# לפני:
def on_start(name, url, nesting_lvl, num_bugs, refactoring, debug, timer_mins):

# אחרי:
def on_start(saved_name, url, nesting_lvl, num_bugs, refactoring, debug, timer_mins, has_env):
```

**ועדכן את השורה שמשתמשת בשם:**

```python
# לפני:
name_str = name.strip()

# אחרי:
name_str = saved_name.strip() if saved_name else "Student"
```

**ועדכן את ה-click:**

```python
start_btn.click(
    on_start,
    inputs=[
        user_name_state if not has_env_key else name_box,  # אם local - name_box, אם hosted - state
        url_box, nesting_slider, bugs_slider, 
        refactoring_check, debug_check, timer_slider,
        gr.State(has_env_key)  # האם זה local או hosted
    ],
    outputs=[...],
)
```

---

## התוצאה:

✅ **Local (.env exists):**
- לא רואה login page
- ישר לsetup page
- אין logout button (לא צריך)

✅ **Hosted (no .env):**
- רואה login page
- צריך להזין API key
- יש logout button בפינה
- אחרי logout חוזר ל-login

---

רוצה שאעשה את השינויים בעצמי בקוד? 🚀
