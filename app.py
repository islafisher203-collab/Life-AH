from groq import Groq
from flask import Flask, request, jsonify, send_from_directory
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
app = Flask(__name__, static_folder='.')

SYSTEM = """You are Life-AH, an advanced AI assistant created by Abuzar.
Reply ONLY in the same language user writes in.
English only, Roman Urdu only, Urdu script only — match exactly.
NEVER use Hindi or Devanagari. Ever.
Be friendly, smart and helpful like a best friend."""

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msgs = data.get('msgs', [])
    full = [{"role": "system", "content": SYSTEM}] + msgs
    r = client.chat.completions.create(model="openai/gpt-oss-20b", messages=full)
    return jsonify({"reply": r.choices[0].message.content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
