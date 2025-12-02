import streamlit as st
import streamlit.components.v1 as components
import random

# --------------------------------------------------------------------------
# CONFIGURATION & STATE
# --------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Digital Flipboard", initial_sidebar_state="expanded")

# Initialize Session State for Playlist
if 'playlist_items' not in st.session_state:
    st.session_state['playlist_items'] = ["WELCOME TO OMNI BOARD", "INSPIRE FROM ANYWHERE", "NOSTALGIA REIMAGINED"]

# --------------------------------------------------------------------------
# ADMIN PANEL (Sidebar)
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("Flipboard Controls")
    
    # --- Message Playlist Manager ---
    st.markdown("### 📝 Message Playlist")
    
    # Display Dynamic Input Boxes
    updated_playlist = []
    for i, item in enumerate(st.session_state['playlist_items']):
        val = st.text_input(f"Message {i+1}", value=item, key=f"msg_input_{i}")
        updated_playlist.append(val.upper())
    
    # Update state with current inputs
    st.session_state['playlist_items'] = updated_playlist

    # Playlist Action Buttons
    col_add, col_reset = st.columns(2)
    if col_add.button("➕ Add Message"):
        st.session_state['playlist_items'].append("")
        st.rerun()
        
    if col_reset.button("🗑️ Clear All"):
        st.session_state['playlist_items'] = [" "]
        st.rerun()

    cycle_speed = st.slider("Cycle Speed (Seconds)", 2, 60, 8)

    st.markdown("---")
    
    # --- Configuration ---
    st.subheader("⚙️ Grid Size")
    rows = st.number_input("Rows", min_value=1, max_value=20, value=6)
    cols = st.number_input("Columns", min_value=1, max_value=50, value=22)
    
    st.markdown("---")

    # --- Art Presets ---
    st.subheader("🎨 Art Presets")
    col_art1, col_art2, col_art3 = st.columns(3)
    
    def generate_pattern(type, rows, cols):
        if type == "OCEAN":
            return "".join([random.choice("🟦🟦🟦🌊") for _ in range(rows*cols)])
        elif type == "SUNRISE":
            colors = ["⬛", "🟥", "🟧", "🟨", "⬜"]
            out = ""
            for r in range(rows):
                idx = int((r / rows) * len(colors))
                out += colors[idx] * cols
            return out
        elif type == "RAINBOW":
            colors = ["🟥","🟧","🟨","🟩","🟦","🟪"]
            out = ""
            for r in range(rows):
                c = colors[r % len(colors)]
                out += c * cols
            return out
        return ""

    # These buttons overwrite the playlist with a single Art Frame
    if col_art1.button("Ocean"):
        st.session_state['playlist_items'] = [generate_pattern("OCEAN", rows, cols)]
        st.rerun()
    if col_art2.button("Sunrise"):
        st.session_state['playlist_items'] = [generate_pattern("SUNRISE", rows, cols)]
        st.rerun()
    if col_art3.button("Rainbow"):
        st.session_state['playlist_items'] = [generate_pattern("RAINBOW", rows, cols)]
        st.rerun()

    st.markdown("---")
    
    # --- Style Options ---
    st.subheader("✨ Style Options")
    
    font_family = st.selectbox("Font Type", [
        "Courier New, monospace", 
        "Arial, sans-serif", 
        "Roboto, sans-serif", 
        "Impact, sans-serif",
        "Segoe UI Emoji, Apple Color Emoji, sans-serif" 
    ])
    
    font_size_mult = st.slider("Font Size Adjustment", 0.5, 2.0, 1.0, help="Scale text size up or down")
    is_bold = st.checkbox("Bold Text", value=True)
    is_italic = st.checkbox("Italic Text", value=False)
    justification = st.selectbox("Justification", ["Left", "Center", "Right"])
    
    col1, col2 = st.columns(2)
    with col1:
        text_color = st.color_picker("Text Color", "#FFFFFF")
    with col2:
        flap_color = st.color_picker("Flap Color", "#111111")
        
    st.info("Double-click the board to toggle Full Screen.")

# --------------------------------------------------------------------------
# LOGIC: MESSAGE PADDING & FORMATTING
# --------------------------------------------------------------------------
# Clean list: remove empty strings if any
clean_playlist = [msg for msg in st.session_state['playlist_items'] if msg]
if not clean_playlist:
    clean_playlist = [" "]

formatted_playlist = []

for msg in clean_playlist:
    # Truncate if message is too long for the entire board
    if len(msg) > (rows * cols):
        msg = msg[:rows*cols]
        
    final_msg = ""
    # Break message into chunks based on column width
    chunks = [msg[i:i+cols] for i in range(0, len(msg), cols)]
    
    # Add empty rows if message is shorter than board height
    if len(chunks) < rows:
        chunks += [""] * (rows - len(chunks))
        
    for chunk in chunks:
        chunk = chunk[:cols] 
        if justification == "Center":
            pad_len = cols - len(chunk)
            left_pad = pad_len // 2
            right_pad = pad_len - left_pad
            final_msg += (" " * left_pad) + chunk + (" " * right_pad)
        elif justification == "Right":
            pad_len = cols - len(chunk)
            final_msg += (" " * pad_len) + chunk
        else: # Left
            final_msg += chunk.ljust(cols)
            
    formatted_playlist.append(final_msg)

# --------------------------------------------------------------------------
# THE FLIPBOARD ENGINE (HTML/CSS/JS)
# --------------------------------------------------------------------------
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        :root {{
            --bg-color: #000; 
            --bezel-color: #0a0a0a;
            --flap-bg: {flap_color};
            --text-color: {text_color};
            --font-family: {font_family};
            --font-weight: {'bold' if is_bold else 'normal'};
            --font-style: {'italic' if is_italic else 'normal'};
            --shadow-intensity: 0.4;
            --font-scale: {font_size_mult};
        }}

        body {{
            background-color: var(--bg-color);
            margin: 0;
            height: 100vh;
            width: 100vw;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: var(--font-family);
            overflow: hidden;
            user-select: none;
        }}

        #board-container {{
            background-color: var(--bezel-color);
            padding: 1.5vmin; 
            border-radius: 1vmin;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8);
            border: 2px solid #222;
            display: grid;
            gap: 0.25vmin; 
            grid-template-columns: repeat({cols}, 1fr); 
            grid-template-rows: repeat({rows}, 1fr);
            
            /* SCALING: Fill 95% of Viewport */
            width: 95vw;
            height: 95vh;
            aspect-ratio: {cols} / {rows * 1.2}; 
            max-width: 100%;
            max-height: 100%;
            cursor: pointer;
        }}

        .split-flap {{
            position: relative;
            width: 100%;
            height: 100%;
            background-color: var(--flap-bg);
            color: var(--text-color);
            border-radius: 0.4vmin;
            
            display: flex;
            justify-content: center;
            align-items: center;
            
            /* Responsive font size multiplied by user slider */
            font-size: calc(4vmin * var(--font-scale)); 
            
            font-weight: var(--font-weight);
            font-style: var(--font-style);
            box-shadow: inset 0 0 5px rgba(0,0,0, var(--shadow-intensity));
            overflow: hidden;
        }}

        .split-flap::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 1px;
            background-color: rgba(0,0,0,0.5);
            z-index: 10;
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

        .top, .next-top {{ top: 0; border-radius: 0.4vmin 0.4vmin 0 0; transform-origin: bottom; }}
        .bottom, .next-bottom {{ bottom: 0; border-radius: 0 0 0.4vmin 0.4vmin; transform-origin: top; }}
        
        .top span, .next-top span {{ display: flex; justify-content: center; align-items: center; height: 200%; transform: translateY(0); }}
        .bottom span, .next-bottom span {{ display: flex; justify-content: center; align-items: center; height: 200%; transform: translateY(-50%); }}

        .flipping .top {{ animation: flip-top 0.15s ease-in forwards; z-index: 3; }}
        .flipping .next-bottom {{ animation: flip-bottom 0.15s ease-out 0.15s forwards; z-index: 2; }}

        @keyframes flip-top {{ 100% {{ transform: rotateX(-90deg); }} }}
        @keyframes flip-bottom {{ 0% {{ transform: rotateX(90deg); }} 100% {{ transform: rotateX(0deg); }} }}
    </style>
</head>
<body ondblclick="toggleFullScreen()">
    <div id="board-container" title="Double Click for Full Screen"></div>

    <script>
        // Safe alphabet for animation phase to prevent glitch glyphs
        const SAFE_CHARS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        
        const ROWS = {rows};
        const COLS = {cols};
        const PLAYLIST = {formatted_playlist};
        const CYCLE_SPEED = {cycle_speed * 1000};

        function toggleFullScreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen().catch(e => {{}});
            }} else {{
                if (document.exitFullscreen) {{
                    document.exitFullscreen();
                }}
            }}
        }}

        class SplitFlap {{
            constructor(element) {{
                this.element = element;
                this.currentChar = " "; 
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
                this.targetChar = char;
                if (this.currentChar !== this.targetChar && !this.isFlipping) {{
                    this.flip();
                }}
            }}

            flip() {{
                if (this.currentChar === this.targetChar) {{
                    this.isFlipping = false;
                    this.updateDOM(this.targetChar, this.targetChar);
                    this.element.classList.remove('flipping');
                    return;
                }}

                this.isFlipping = true;

                // Pick a visual character for the flip (noise) to prevent ? glitches
                let currentIndex = SAFE_CHARS.indexOf(this.currentChar);
                if (currentIndex === -1) currentIndex = 0;
                let nextIndex = (currentIndex + 1) % SAFE_CHARS.length;
                let nextVisualChar = SAFE_CHARS[nextIndex];

                const nextTop = this.element.querySelector('.next-top span');
                const nextBottom = this.element.querySelector('.next-bottom span');
                nextTop.innerText = nextVisualChar;
                nextBottom.innerText = nextVisualChar;

                this.element.classList.add('flipping');

                setTimeout(() => {{
                    this.updateDOM(nextVisualChar, nextVisualChar);
                    this.currentChar = nextVisualChar;
                    this.element.classList.remove('flipping');

                    // Random chance to snap to target or keep spinning
                    if (Math.random() > 0.85 || this.currentChar === this.targetChar) {{
                         this.currentChar = this.targetChar;
                         this.updateDOM(this.targetChar, this.targetChar);
                         this.isFlipping = false;
                    }} else {{
                        setTimeout(() => this.flip(), 60); 
                    }}
                }}, 150);
            }}

            updateDOM(topChar, bottomChar) {{
                this.element.querySelector('.top span').innerText = topChar;
                this.element.querySelector('.bottom span').innerText = bottomChar;
                this.element.querySelector('.next-top span').innerText = topChar;
                this.element.querySelector('.next-bottom span').innerText = bottomChar;
            }}
        }}

        let grid = [];

        function initBoard() {{
            const container = document.getElementById('board-container');
            container.innerHTML = '';
            grid = [];

            for (let i = 0; i < ROWS * COLS; i++) {{
                const div = document.createElement('div');
                div.className = 'split-flap';
                container.appendChild(div);
                grid.push(new SplitFlap(div));
            }}
            cycleMessages();
        }}

        let msgIndex = 0;
        function cycleMessages() {{
            if (PLAYLIST.length === 0) return;
            const msg = PLAYLIST[msgIndex];
            const charArray = Array.from(msg);
            
            grid.forEach((flap, index) => {{
                if (index < charArray.length) {{
                    flap.setTarget(charArray[index]);
                }} else {{
                    flap.setTarget(" ");
                }}
            }});

            msgIndex = (msgIndex + 1) % PLAYLIST.length;
            setTimeout(cycleMessages, CYCLE_SPEED);
        }}

        initBoard();
    </script>
</body>
</html>
"""

st.markdown("""
<style>
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100%;
    }
    iframe {
        width: 100vw;
        height: 100vh;
        border: none;
        display: block;
    }
    footer {visibility: hidden;}
    /* Show header only on hover */
    header {opacity: 0; transition: opacity 0.3s;}
    header:hover {opacity: 1;}
</style>
""", unsafe_allow_html=True)

components.html(html_code, height=900, scrolling=False)
