from flask import Flask, request, jsonify
from server import MainExecution
import os
import json
from difflib import get_close_matches

app = Flask(__name__)

device_app_map = {}
DEVICE_APPS_DIR = "device_apps"

@app.route("/connect", methods=["GET"])
def connect_test():
    return jsonify({"status": "connected"}), 200

@app.route('/device_apps', methods=['POST'])
def device_apps():
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400
    os.makedirs(DEVICE_APPS_DIR, exist_ok=True)
    apps_json = request.get_data(as_text=True)
    with open(os.path.join(DEVICE_APPS_DIR, f"{device_id}.json"), "w", encoding="utf-8") as f:
        f.write(apps_json)
    return jsonify({"status": "ok"})

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

    # MainExecution now returns a dict with 'response' and 'device_action'
    result = MainExecution(query, device_id)
    if isinstance(result, dict):
        response_data = {
            "response": result.get("response", "Done."),
            "device_action": result.get("device_action", "")
        }
    else:
        # fallback for legacy tuple return
        try:
            final_output, device_action = result
            response_data = {
                "response": final_output or "Done.",
                "device_action": device_action if isinstance(device_action, str) else (device_action.get("command", "") if device_action else "")
            }
        except Exception:
            response_data = {
                "response": str(result),
                "device_action": ""
            }

    # If modal decided to open an app, check if it's actually available on device
    if response_data["device_action"] and isinstance(response_data["device_action"], str) and response_data["device_action"].startswith("open::") and device_id:
        appname = response_data["device_action"].split("::")[1].strip()
        best_app = find_best_app_match(f"open {appname}", device_id)
        if best_app:
            response_data["device_action"] = f"open::{best_app}"
        else:
            response_data["device_action"] = ""

    print("[DEBUG] Final response data:", response_data)
    return jsonify(response_data), 200

if __name__ == "__main__":
    print("[INFO] Starting Flask server on http://0.0.0.0:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
