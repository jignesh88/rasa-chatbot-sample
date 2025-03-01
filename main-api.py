from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)


@app.route("/chat", methods=["POST"])
def chat():
    print(request.json)
    user_message = request.json.get("message", "")
    sender_id = request.json.get("sender_id", "default_user")

    # Send to RASA
    rasa_url = "http://localhost:5005/webhooks/rest/webhook"
    payload = {"sender": sender_id, "message": user_message}

    headers = {"Content-Type": "application/json"}
    response = requests.post(rasa_url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify([{"text": f"Error: {response.status_code}"}])


if __name__ == "__main__":
    app.run(debug=True, port=8000)
