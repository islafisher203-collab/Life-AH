from groq import Groq
from flask import Flask, request, jsonify, send_from_directory
import os
import urllib.parse
import requests as req

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
HF_TOKEN = os.environ.get("HF_TOKEN", "")
app = Flask(__name__, static_folder='.')

SYSTEM = """You are Life-AH, an advanced AI assistant created by Abuzar.
Reply ONLY in the same language user writes in.
English only, Roman Urdu only, Urdu script only — match exactly.
NEVER use Hindi or Devanagari. Ever.
Be friendly, smart and helpful like a best friend.

IMPORTANT: If the user asks to draw, create, generate, or make an image/photo/picture,
reply with ONLY this exact format on the first line:
IMAGE_REQUEST: <detailed english description of the image>
Then on the next line write a short friendly message saying you are generating it."""

def generate_image(prompt):
    try:
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "blurry, low quality, distorted, ugly",
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 1024,
                "height": 1024
            }
        }
        response = req.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            import base64
            img_data = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/jpeg;base64,{img_data}"
        else:
            encoded = urllib.parse.quote(prompt)
            return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true"
    except Exception as e:
        encoded = urllib.parse.quote(prompt)
        return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true"

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
        image_url = generate_image(prompt)
        reply = friendly_msg

    return jsonify({"reply": reply, "image_url": image_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
