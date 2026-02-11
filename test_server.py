from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

EVENTS_FILE = 'events.json'

def load_events():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_events(events):
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)

events = load_events()

@app.route('/api/data', methods=['GET', 'POST'])
def receive_data():
    global events
    if request.method == 'POST':
        data = request.get_json()
        print(json.dumps(data))
        events.append(data)
        save_events(events)
        return jsonify({"status": "success"}), 200
    else:
        return jsonify(events), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)