from flask import Flask, request, jsonify
import openai
import requests
import os

app = Flask(__name__)

ZAPI_ID = os.getenv("ZAPI_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_ID}/token/{ZAPI_TOKEN}/send-text"

openai.api_key = OPENAI_API_KEY

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        message = data.get("text", {}).get("message", "")
        phone = data.get("phone", "")

        if not message or not phone:
            return jsonify({"error": "Mensagem ou número de telefone ausente"}), 400

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )

        reply = response['choices'][0]['message']['content']

        payload = {
            "phone": phone,
            "message": reply
        }

        requests.post(ZAPI_URL, json=payload)
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)