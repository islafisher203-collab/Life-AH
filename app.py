from groq import Groq
from flask import Flask, request, jsonify, send_from_directory
import os
import urllib.parse
import requests as req
import base64

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
Then on the next line write a short friendly message."""

def generate_image(prompt):
    try:
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "blurry, low quality, distorted",
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 1024,
                "height": 1024
            }
        }
        response = req.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            img_data = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/jpeg;base64,{img_data}"
    except:
        pass
    encoded = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true"

def analyze_and_edit(image_base64, instruction):
    try:
        if ',' in image_base64:
            img_data = image_base64.split(',')[1]
        else:
            img_data = image_base64

        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
                        },
                        {
                            "type": "text",
                            "text": f"Describe this image in detail, then create a new image generation prompt that includes all original details but with this edit applied: '{instruction}'. Output ONLY the new prompt, nothing else."
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        new_prompt = response.choices[0].message.content.strip()
        return generate_image(new_prompt), new_prompt
    except Exception as e:
        return None, str(e)

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

@app.route('/edit', methods=['POST'])
def edit():
    data = request.json
    image = data.get('image', '')
    instruction = data.get('instruction', 'enhance this image')
    result, prompt = analyze_and_edit(image, instruction)
    if result:
        reply = "Ye rahi edited photo! 🎨"
    else:
        reply = f"Error: {prompt}"
    return jsonify({"reply": reply, "image_url": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
