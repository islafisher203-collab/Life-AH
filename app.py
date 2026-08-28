from groq import Groq
from flask import Flask, request, jsonify, send_from_directory
import os
import urllib.parse

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
app = Flask(__name__, static_folder='.')

SYSTEM = """You are Life-AH, an advanced AI assistant created by Abuzar.
Reply ONLY in the same language user writes in.
English only, Roman Urdu only, Urdu script only — match exactly.
NEVER use Hindi or Devanagari. Ever.
Be friendly, smart and helpful like a best friend.

IMPORTANT: If the user asks to draw, create, generate, or make an image/photo/picture, 
reply with ONLY this exact format on the first line:
IMAGE_REQUEST: <english description of the image>
Then on the next line write a short friendly message saying you are generating it."""

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msgs = data.get('msgs', [])
    full = [{"role": "system", "content": SYSTEM}] + msgs
    r = client.chat.completions.create(model="openai/gpt-oss-20b", messages=full)
    reply = r.choices[0].message.content

    image_url = None
    if reply.startswith("IMAGE_REQUEST:"):
        lines = reply.split('\n', 1)
        prompt = lines[0].replace("IMAGE_REQUEST:", "").strip()
        friendly_msg = lines[1].strip() if len(lines) > 1 else "Generating your image..."
        encoded = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true"
        reply = friendly_msg

    return jsonify({"reply": reply, "image_url": image_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
