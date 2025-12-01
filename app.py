# app.py
from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

# DATA PERSISTENCE
CONFIG_FILE = 'board_state.json'

# Default Configuration
default_state = {
    "rows": 6,
    "cols": 22,
    "theme": "black",  # or 'white'
    "current_message": "WELCOME TO OMNI BOARD",
    "speed": 150 # ms per flip
}

def load_state():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return default_state

def save_state(state):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(state, f)

current_state = load_state()

@app.route('/')
def board():
    return render_template('board.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# API ENDPOINTS
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(current_state)

@app.route('/api/configure', methods=['POST'])
def configure_board():
    global current_state
    data = request.json
    current_state['rows'] = int(data.get('rows', current_state['rows']))
    current_state['cols'] = int(data.get('cols', current_state['cols']))
    current_state['theme'] = data.get('theme', current_state['theme'])
    save_state(current_state)
    return jsonify({"status": "success", "state": current_state})

@app.route('/api/message', methods=['POST'])
def update_message():
    global current_state
    data = request.json
    current_state['current_message'] = data.get('message', '').upper()
    save_state(current_state)
    return jsonify({"status": "success", "message": current_state['current_message']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)