/* static/script.js */

// The Character Wheel (Order matters for rotation)
const CHARS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&?.:-";

class SplitFlap {
    constructor(element) {
        this.element = element;
        this.currentChar = " ";
        this.targetChar = " ";
        this.isFlipping = false;
        
        // Create internal DOM structure
        this.element.innerHTML = `
            <div class="top"><span> </span></div>
            <div class="bottom"><span> </span></div>
            <div class="next-top"><span> </span></div>
            <div class="next-bottom"><span> </span></div>
        `;
    }

    setTarget(char) {
        // Normalize input
        if (!CHARS.includes(char)) char = " ";
        this.targetChar = char;
        if (this.currentChar !== this.targetChar && !this.isFlipping) {
            this.flip();
        }
    }

    flip() {
        if (this.currentChar === this.targetChar) {
            this.isFlipping = false;
            return;
        }

        this.isFlipping = true;
        
        // Find next char in the wheel
        let currentIndex = CHARS.indexOf(this.currentChar);
        let nextIndex = (currentIndex + 1) % CHARS.length;
        let nextChar = CHARS[nextIndex];

        // Update invisible 'next' flaps
        const nextTop = this.element.querySelector('.next-top span');
        const nextBottom = this.element.querySelector('.next-bottom span');
        nextTop.innerText = nextChar;
        nextBottom.innerText = nextChar;

        // Trigger animation
        this.element.classList.add('flipping');

        // Halfway through animation (after top falls), update 'current'
        setTimeout(() => {
            // This timeout matches CSS animation duration
            const top = this.element.querySelector('.top span');
            const bottom = this.element.querySelector('.bottom span');
            
            top.innerText = nextChar;
            bottom.innerText = nextChar;
            
            this.currentChar = nextChar;
            this.element.classList.remove('flipping');

            // Recursive call to keep flipping if not at target
            if (this.currentChar !== this.targetChar) {
                // Slight delay for realism vs speed
                setTimeout(() => this.flip(), 30); 
            } else {
                this.isFlipping = false;
            }
        }, 300); // 150ms * 2 for full flip cycle
    }
}

let boardGrid = [];

async function initBoard() {
    const response = await fetch('/api/status');
    const state = await response.json();
    
    const container = document.getElementById('board-container');
    document.body.className = `theme-${state.theme}`;
    
    // Set Grid CSS
    container.style.gridTemplateColumns = `repeat(${state.cols}, 1fr)`;
    container.innerHTML = '';
    boardGrid = [];

    // Create Grid
    for (let i = 0; i < state.rows * state.cols; i++) {
        const div = document.createElement('div');
        div.className = 'split-flap';
        container.appendChild(div);
        boardGrid.push(new SplitFlap(div));
    }

    updateBoard(state.current_message);
}

function updateBoard(message) {
    // Pad message to fit grid
    const totalCells = boardGrid.length;
    let paddedMessage = message.padEnd(totalCells, " ");
    
    // Or center logic (optional)
    // const padding = Math.floor((totalCells - message.length) / 2);
    // paddedMessage = " ".repeat(Math.max(0, padding)) + message;
    // paddedMessage = paddedMessage.padEnd(totalCells, " ");

    boardGrid.forEach((flap, index) => {
        if (index < paddedMessage.length) {
            flap.setTarget(paddedMessage[index]);
        } else {
            flap.setTarget(" ");
        }
    });
}

// Polling for updates
setInterval(async () => {
    const response = await fetch('/api/status');
    const state = await response.json();
    
    // Check if theme or dimensions changed (naive reload)
    const container = document.getElementById('board-container');
    const currentCols = container.style.gridTemplateColumns.split(' ').length;
    
    // If config changed, hard reload grid
    if (boardGrid.length !== state.rows * state.cols) {
        initBoard(); // Re-init grid
    } else {
        // Just update message and theme
        if(!document.body.classList.contains(`theme-${state.theme}`)) {
            document.body.className = `theme-${state.theme}`;
        }
        updateBoard(state.current_message);
    }
}, 2000); // Poll every 2 seconds

// Initial Load
document.addEventListener('DOMContentLoaded', initBoard);

// Full Screen Toggle
document.addEventListener('click', () => {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(e => console.log(e));
    }
});