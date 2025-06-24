import os
import requests
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Variáveis de ambiente (Render)
ZAPI_ID = os.environ.get("ZAPI_ID")
ZAPI_TOKEN = os.environ.get("ZAPI_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

ZAPI_BASE_URL = f"https://api.z-api.io/instances/{ZAPI_ID}/token/{ZAPI_TOKEN}/send-text"

@app.route("/", methods=["GET"])
def home():
    return "Bot está online!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Verifica se é mensagem recebida
    if data.get("type") != "ReceivedCallback":
        return jsonify({"status": "ignorado"})

    phone = data.get("phone")
    message = data.get("text", {}).get("message", "")

    if not phone or not message:
        return jsonify({"error": "mensagem ou número ausente"})

    print(f"Mensagem recebida de {phone}: {message}")

    # Gera resposta da IA
    resposta = gerar_resposta_com_ia(message)

    # Envia a resposta para o WhatsApp
    enviar_mensagem_whatsapp(phone, resposta)

    return jsonify({"status": "mensagem processada"})

def gerar_resposta_com_ia(pergunta):
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um atendente educado e prestativo de uma gráfica."},
                {"role": "user", "content": pergunta}
            ],
            temperature=0.7
        )
        return resposta['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("Erro ao gerar resposta da IA:", e)
        return "Desculpe, não consegui responder agora."

def enviar_mensagem_whatsapp(phone, mensagem):
    payload = {
        "phone": phone,
        "message": mensagem
    }
    try:
        r = requests.post(ZAPI_BASE_URL, json=payload)
        print("Mensagem enviada:", r.status_code)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
