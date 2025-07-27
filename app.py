from flask import Flask, request, jsonify
from test_model import MainExecution
import os
import json
from difflib import get_close_matches
import asyncio

app = Flask(__name__)

@app.route("/connect", methods=["GET"])
async def connect_test():
    return jsonify({"status": "connected"}), 200

@app.route("/device_apps", methods=["POST"])
async def receive_device_apps():
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    apps = request.json
    os.makedirs("device_apps", exist_ok=True)
    try:
        with open(f"device_apps/{device_id}.json", "w") as f:
            json.dump(apps, f, indent=4)
        return jsonify({"status": "App list received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_device_apps/<device_id>', methods=['GET'])
async def get_device_apps(device_id):
    try:
        with open(f"device_apps/{device_id}.json", "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"error": "Device not found"}), 404

def find_best_app_match(spoken_cmd, device_id):
    json_path = f"device_apps/{device_id}.json"
    if not os.path.exists(json_path):
        return None
    with open(json_path, 'r') as file:
        data = json.load(file)
    app_list = list(data.keys())
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
async def ask_jarvis():
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
            "tts_text": f"Opening {best_app.capitalize()}",
            "device_command": f"open::{best_app}"
        }
        print("[DEBUG] App match found, returning:", response_data)
        return jsonify(response_data), 200

    # Fallback to MainExecution
    final_output, device_action = await MainExecution(query, device_id)
    print("[DEBUG] device_action returned from MainExecution:", device_action)

# Remove any tags like [General] from tts_text
    import re
    raw_tts = device_action.get("tts_text", final_output or "Done.")
    clean_tts = re.sub(r"\[.*?\]\s*", "", raw_tts).strip()

    response_data = {
        "tts_text": clean_tts,
        "device_command": device_action.get("device_command", "")
    }
    print("[DEBUG] Returning:", response_data)
    return jsonify(response_data), 200


if __name__ == "__main__":
    print("[INFO] Starting Flask server on http://0.0.0.0:5000 ...")
    from asyncio import run
    app.run(host="0.0.0.0", port=5000, debug=True)