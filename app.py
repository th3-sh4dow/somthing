from flask import Flask, request, jsonify
from server import MainExecution
import os
import json
from difflib import get_close_matches

app = Flask(__name__)

device_app_map = {}

@app.route("/connect", methods=["GET"])
def connect_test():
    return jsonify({"status": "connected"}), 200

@app.route('/device_apps', methods=['POST'])
def receive_apps():
    data = request.get_json()
    device_id = request.headers.get('Device-ID', 'default_device')
    device_app_map[device_id] = data
    print(f"[✅] App list updated for {device_id}")
    return jsonify({"status": "received"}), 200

@app.route('/get_device_apps/<device_id>', methods=['GET'])
def get_device_apps(device_id):
    if device_id in device_app_map:
        return jsonify(device_app_map[device_id])
    return jsonify({"error": "Device not found"}), 404

def find_best_app_match(spoken_cmd, device_id):
    json_path = f"installed_apps/{device_id}.json"
    if not os.path.exists(json_path):
        return None
    with open(json_path, 'r') as file:
        data = json.load(file)
    app_list = data.get("apps", [])
    spoken_cmd = spoken_cmd.lower().strip()
    if spoken_cmd.startswith("open "):
        target_app = spoken_cmd.replace("open ", "").strip()
    else:
        return None
    matches = get_close_matches(target_app, [app.lower() for app in app_list], n=1, cutoff=0.6)
    if matches:
        best_match = matches[0]
        for app in app_list:
            if app.lower() == best_match:
                return app
    return None

@app.route("/ask", methods=["POST"])
def ask_jarvis():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query'"}), 400

    query = data['query']
    device_id = data.get('device_id', None)

    print(f"[DEBUG] Received query from device: {device_id} → {query}")

    # Smart app open logic
    best_app = find_best_app_match(query, device_id) if device_id else None
    if best_app:
        response_data = {
            "response": f"Opening {best_app}",
            "device_action": f"open::{best_app}"
        }
        print("[DEBUG] App match found, returning:", response_data)
        return jsonify(response_data), 200

    # fallback to MainExecution if not an app open command or no match
    final_output, device_action = MainExecution(query, device_id)
    response_data = {
        "response": final_output or "Done.",
        "device_action": device_action["command"] if device_action and "command" in device_action else ""
    }
    print("[DEBUG] Returning:", response_data)
    return jsonify(response_data), 200

if __name__ == "__main__":
    print("[INFO] Starting Flask server on http://0.0.0.0:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
