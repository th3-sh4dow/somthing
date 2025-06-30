from flask import Flask, request, jsonify
from server import MainExecution

app = Flask(__name__)

@app.route("/connect", methods=["GET"])
def connect_test():
    return jsonify({"status": "connected"}), 200

@app.route("/ask", methods=["POST"])
def ask_jarvis():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query'"}), 400

    query = data['query']
    print(f"[REQUEST] User Query: {query}")

    result = MainExecution(query)
    print(f"[RESPONSE - Full] {result}")

    # Step 1: Get the response text
    if isinstance(result, dict):
        raw_response = result.get("response", "No reply")
    else:
        raw_response = str(result)

    # Step 2: Clean response (remove things like "[General Answer]")
    import re
    clean_response = re.sub(r"\[.*?\]\s*", "", raw_response).strip()

    print(f"[RESPONSE - Sent to Android] {clean_response}")
    return jsonify({"response": clean_response})


if __name__ == "__main__":
    print("[INFO] Starting Flask server...")
    app.run(host="0.0.0.0", port=5000, debug=True)


