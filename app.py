import streamlit as st
import streamlit.components.v1 as components
import random

# --------------------------------------------------------------------------
# CONFIGURATION & STATE
# --------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Digital Flipboard", initial_sidebar_state="expanded")

# Initialize Session State for Playlist
if 'playlist_items' not in st.session_state:
    st.session_state['playlist_items'] = [
        "WELCOME TO\nOMNI BOARD", 
        "INSPIRE FROM\nANYWHERE"
    ]

# --------------------------------------------------------------------------
# ADMIN PANEL (Sidebar)
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("Flipboard Controls")
    
    # --- Configuration ---
    st.subheader("⚙️ Grid Size")
    # We place grid size first so Art generation knows the dimensions
    rows = st.number_input("Rows", min_value=1, max_value=20, value=6)
    cols = st.number_input("Columns", min_value=1, max_value=50, value=22)
    
    st.markdown("---")
    
    # --- Message Playlist Manager ---
    st.markdown("### 📝 Message Playlist")
    
    # Display Dynamic Input Boxes (Text Areas for Multi-line)
    updated_playlist = []
    # Iterate over a copy to allow safe modification if needed
    for i, item in enumerate(st.session_state['playlist_items']):
        # We use a unique key for each text area
        val = st.text_area(f"Message {i+1}", value=item, key=f"msg_input_{i}", height=68)
        updated_playlist.append(val.upper())
    
    # Sync state
    st.session_state['playlist_items'] = updated_playlist

    # Playlist Action Buttons
    col_add, col_reset = st.columns(2)
    if col_add.button("➕ Add New"):
        st.session_state['playlist_items'].append("")
        st.rerun()
        
    if col_reset.button("🗑️ Clear All"):
        st.session_state['playlist_items'] = [""]
        st.rerun()

    cycle_speed = st.slider("Cycle Speed (Seconds)", 2, 60, 8)

    st.markdown("---")

    # --- Art Presets ---
    st.subheader("🎨 Art Presets")
    st.caption("Clicking adds art to the end of your playlist.")
    col_art1, col_art2, col_art3 = st.columns(3)
    
    def generate_pattern(type, rows, cols):
        if type == "OCEAN":
            # Random scattering of blue and wave emojis
            return "".join([random.choice("🟦🟦🟦🌊") for _ in range(rows*cols)])
        elif type == "SUNRISE":
            # Vertical gradient approximation
            colors = ["⬛", "🟥", "🟧", "🟨", "⬜"]
            out = ""
            for r in range(rows):
                idx = int((r / rows) * len(colors))
                # Safe index check
                idx = min(idx, len(colors)-1)
                out += colors[idx] * cols
            return out
        elif type == "RAINBOW":
            # Horizontal stripes
            colors = ["🟥","🟧","🟨","🟩","🟦","🟪"]
            out = ""
            for r in range(rows):
                c = colors[r % len(colors)]
                out += c * cols
            return out
        return ""

    # ACTION: APPEND instead of overwrite
    if col_art1.button("Ocean"):
        art_str = generate_pattern("OCEAN", rows, cols)
        st.session_state['playlist_items'].append(art_str)
        st.rerun()
        
    if col_art2.button("Sunrise"):
        art_str = generate_pattern("SUNRISE", rows, cols)
        st.session_state['playlist_items'].append(art_str)
        st.rerun()
        
    if col_art3.button("Rainbow"):
        art_str = generate_pattern("RAINBOW", rows, cols)
        st.session_state['playlist_items'].append(art_str)
        st.rerun()

    st.markdown("---")
    
    # --- Style Options ---
    st.subheader("✨ Style Options")
    
    font_family_selection = st.selectbox("Font Type", [
        "Courier New", 
        "Arial", 
        "Roboto", 
        "Impact",
        "Verdana" 
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
# LOGIC: MULTI-LINE MESSAGE FORMATTING
# --------------------------------------------------------------------------
clean_playlist = [msg for msg in st.session_state['playlist_items'] if msg]
if not clean_playlist:
    clean_playlist = [" "]

formatted_playlist = []

for raw_msg in clean_playlist:
    final_string = ""
    current_rows = 0
    
    # 1. Split by manual newlines first
    manual_lines = raw_msg.split('\n')
    
    for line in manual_lines:
        if current_rows >= rows:
            break
            
        # 2. Handle lines longer than 'cols' (Auto-wrap)
        if len(line) > 0:
            line_chunks = [line[i:i+cols] for i in range(0, len(line), cols)]
        else:
            line_chunks = [""] 

        for chunk in line_chunks:
            if current_rows >= rows:
                break
                
            # 3. Apply Justification/Padding to the chunk
            chunk = chunk[:cols]
            
            # IMPORTANT: Emojis are typically length 1 in Python strings (mostly),
            # but if they aren't, justification might look slightly off in the preview string.
            # However, the grid mapping in JS handles them character-by-character.
            
            pad_len = cols - len(chunk)
            
            if justification == "Center":
                left_pad = pad_len // 2
                right_pad = pad_len - left_pad
                row_str = (" " * left_pad) + chunk + (" " * right_pad)
            elif justification == "Right":
                row_str = (" " * pad_len) + chunk
            else: # Left
                row_str = chunk.ljust(cols)
            
            final_string += row_str
            current_rows += 1

    # 4. Fill remaining rows on the board with empty space
    remaining_rows = rows - current_rows
    if remaining_rows > 0:
        final_string += (" " * cols) * remaining_rows
    
    # 5. Truncate to ensure perfect grid fit
    final_string = final_string[:rows * cols]
    
    formatted_playlist.append(final_string)

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
            
            /* FONT STACK FIX: Force Emoji fonts to load if main font misses the glyph */
            --font-family: '{font_family_selection}', "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif;
            
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
        // "Visual Noise" characters for animation. Pure Alphanumeric to prevent missing glyphs during flip.
        const SAFE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        
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

                // Animation Logic:
                // 1. Pick a random "Safe" character to show during the flip motion (blur effect)
                // 2. This avoids showing '?' boxes if the browser tries to render an emoji in a non-emoji font during transition
                let nextVisualChar = SAFE_CHARS[Math.floor(Math.random() * SAFE_CHARS.length)];

                const nextTop = this.element.querySelector('.next-top span');
                const nextBottom = this.element.querySelector('.next-bottom span');
                
                // During animation, show the Safe Char
                nextTop.innerText = nextVisualChar;
                nextBottom.innerText = nextVisualChar;

                this.element.classList.add('flipping');

                setTimeout(() => {{
                    // Frame complete. Update static flaps to the char we just flipped to
                    this.updateDOM(nextVisualChar, nextVisualChar);
                    this.currentChar = nextVisualChar;
                    this.element.classList.remove('flipping');

                    // Check if we should stop
                    // 15% chance to snap to target to simulate mechanical randomness
                    // OR if we somehow accidentally landed on the target
                    if (Math.random() > 0.85 || this.currentChar === this.targetChar) {{
                         this.currentChar = this.targetChar;
                         // Force the actual target char (Emoji or Text) into the DOM
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
            // Split using Array.from ensures surrogate pair Emojis are treated as 1 char
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
    header {opacity: 0; transition: opacity 0.3s;}
    header:hover {opacity: 1;}
</style>
""", unsafe_allow_html=True)

components.html(html_code, height=900, scrolling=False)
