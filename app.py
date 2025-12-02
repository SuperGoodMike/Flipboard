import streamlit as st
import streamlit.components.v1 as components

# --------------------------------------------------------------------------
# CONFIGURATION & STATE
# --------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Digital Flipboard", initial_sidebar_state="collapsed")

# Initialize Session State for persistence across re-runs
if 'message' not in st.session_state:
    st.session_state['message'] = "WELCOME TO OMNI BOARD"
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'black'

# --------------------------------------------------------------------------
# ADMIN PANEL (Sidebar)
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("Flipboard Controls")
    
    # Message Input
    new_msg = st.text_input("Message", value=st.session_state['message'], max_chars=132)
    if new_msg != st.session_state['message']:
        st.session_state['message'] = new_msg.upper()
        
    # Configuration
    st.markdown("---")
    st.subheader("Display Settings")
    rows = st.number_input("Rows", min_value=1, max_value=20, value=6)
    cols = st.number_input("Columns", min_value=1, max_value=50, value=22)
    
    theme_val = st.selectbox("Theme", ["Vestaboard Black", "Vestaboard White"])
    st.session_state['theme'] = "black" if "Black" in theme_val else "white"
    
    st.info("Tip: Close this sidebar using the 'X' or arrow to see the board in Full Screen.")

# --------------------------------------------------------------------------
# THE FLIPBOARD ENGINE (HTML/CSS/JS)
# --------------------------------------------------------------------------
# We inject the Python variables (rows, cols, message) directly into the JS
# This replaces the need for the Flask API.

html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        :root {{
            --bg-color: #111;
            --bezel-color: #0a0a0a;
            --flap-bg: #1e1e1e;
            --text-color: #f0f0f0;
            --shadow-intensity: 0.6;
        }}

        body.theme-white {{
            --bg-color: #f4f4f4;
            --bezel-color: #e0e0e0;
            --flap-bg: #ffffff;
            --text-color: #222;
            --shadow-intensity: 0.2;
        }}

        body {{
            background-color: var(--bg-color);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Courier New', Courier, monospace;
            overflow: hidden;
        }}

        #board-container {{
            background-color: var(--bezel-color);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            border: 2px solid #333;
            display: grid;
            gap: 4px;
            perspective: 1000px;
            /* Dynamic Columns */
            grid-template-columns: repeat({cols}, 1fr); 
        }}

        .split-flap {{
            position: relative;
            width: 40px; /* Sized down slightly for browser embedding */
            height: 60px;
            font-size: 35px;
            line-height: 60px;
            text-align: center;
            color: var(--text-color);
            background-color: var(--flap-bg);
            border-radius: 3px;
            box-shadow: inset 0 0 5px rgba(0,0,0, var(--shadow-intensity));
        }}

        .split-flap::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 1px;
            background-color: rgba(0,0,0,0.4);
            z-index: 5;
        }}

        .top, .bottom, .next-top, .next-bottom {{
            position: absolute;
            left: 0;
            width: 100%;
            height: 50%;
            overflow: hidden;
            background-color: var(--flap-bg);
            backface-visibility: hidden;
        }}

        .top, .next-top {{ top: 0; border-radius: 3px 3px 0 0; transform-origin: bottom; }}
        .bottom, .next-bottom {{ bottom: 0; border-radius: 0 0 3px 3px; transform-origin: top; }}
        
        .top span, .next-top span {{ display: block; height: 200%; }}
        .bottom span, .next-bottom span {{ display: block; height: 200%; transform: translateY(-50%); }}

        .flipping .top {{ animation: flip-top 0.15s ease-in forwards; z-index: 3; }}
        .flipping .next-bottom {{ animation: flip-bottom 0.15s ease-out 0.15s forwards; z-index: 2; }}

        @keyframes flip-top {{ 100% {{ transform: rotateX(-90deg); }} }}
        @keyframes flip-bottom {{ 0% {{ transform: rotateX(90deg); }} 100% {{ transform: rotateX(0deg); }} }}
    </style>
</head>
<body class="theme-{st.session_state['theme']}">
    <div id="board-container"></div>

    <script>
        const CHARS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&?.:-";
        const ROWS = {rows};
        const COLS = {cols};
        // We inject the message from Python
        const TARGET_MESSAGE = "{st.session_state['message']}"; 

        class SplitFlap {{
            constructor(element) {{
                this.element = element;
                this.currentChar = " "; // Start Blank
                this.targetChar = " ";
                this.isFlipping = false;
                
                this.element.innerHTML = `
                    <div class="top"><span> </span></div>
                    <div class="bottom"><span> </span></div>
                    <div class="next-top"><span> </span></div>
                    <div class="next-bottom"><span> </span></div>
                `;
            }}

            setTarget(char) {{
                if (!CHARS.includes(char)) char = " ";
                this.targetChar = char;
                if (this.currentChar !== this.targetChar && !this.isFlipping) {{
                    this.flip();
                }}
            }}

            flip() {{
                if (this.currentChar === this.targetChar) {{
                    this.isFlipping = false;
                    return;
                }}
                this.isFlipping = true;
                
                let currentIndex = CHARS.indexOf(this.currentChar);
                let nextIndex = (currentIndex + 1) % CHARS.length;
                let nextChar = CHARS[nextIndex];

                const nextTop = this.element.querySelector('.next-top span');
                const nextBottom = this.element.querySelector('.next-bottom span');
                nextTop.innerText = nextChar;
                nextBottom.innerText = nextChar;

                this.element.classList.add('flipping');

                setTimeout(() => {{
                    const top = this.element.querySelector('.top span');
                    const bottom = this.element.querySelector('.bottom span');
                    top.innerText = nextChar;
                    bottom.innerText = nextChar;
                    this.currentChar = nextChar;
                    this.element.classList.remove('flipping');

                    if (this.currentChar !== this.targetChar) {{
                        setTimeout(() => this.flip(), 20); // Speed of flip
                    }} else {{
                        this.isFlipping = false;
                    }}
                }}, 300); // Animation duration match
            }}
        }}

        function initBoard() {{
            const container = document.getElementById('board-container');
            container.innerHTML = '';
            let grid = [];

            for (let i = 0; i < ROWS * COLS; i++) {{
                const div = document.createElement('div');
                div.className = 'split-flap';
                container.appendChild(div);
                grid.push(new SplitFlap(div));
            }}

            // Apply Message
            // We use a slight delay so the user sees it flip from blank to text
            setTimeout(() => {{
                let paddedMessage = TARGET_MESSAGE.padEnd(ROWS * COLS, " ");
                grid.forEach((flap, index) => {{
                    if (index < paddedMessage.length) {{
                        flap.setTarget(paddedMessage[index]);
                    }}
                }});
            }}, 500);
        }}

        // Run on load
        initBoard();
    </script>
</body>
</html>
"""

# --------------------------------------------------------------------------
# STREAMLIT UI HACKS (Full Screen Look)
# --------------------------------------------------------------------------
# Remove the white padding Streamlit adds, so the board touches the edges
st.markdown("""
<style>
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }
    iframe {
        width: 100%;
        border: none;
    }
    /* Hide the Streamlit Header and Footer for immersion */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Render the Board
# We set a high height to accommodate the grid. 
# In a real deployed app, you might adjust this based on rows.
components.html(html_code, height=900, scrolling=False)
