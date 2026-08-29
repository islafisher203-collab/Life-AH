from groq import Groq
from flask import Flask, request, jsonify, send_from_directory
import os
import base64
import random

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
app = Flask(__name__, static_folder='.')

SYSTEM = """You are Life-AH, a smart and friendly AI assistant created by Abuzar.

LANGUAGE RULES:
- Users write in Roman Urdu mixed with English — Pakistani style. Match it exactly.
- If user writes Roman Urdu → reply Roman Urdu
- If user writes English → reply English  
- If user writes Urdu script → reply Urdu script
- NEVER use Hindi or Devanagari
- Be casual like a real Pakistani dost — use yaar, bhai naturally

IMAGE GENERATION — if user asks to draw/create/generate any image:
Reply EXACTLY like this (first line must start with IMAGE_REQUEST:):
IMAGE_REQUEST: <detailed english description>
<friendly message>"""

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
                            "text": f"Describe this image in great detail. Then write a new image generation prompt keeping ALL original details but applying: '{instruction}'. Output ONLY the prompt. No thinking tags."
                        }
                    ]
                }
            ],
            max_tokens=400
        )
        new_prompt = response.choices[0].message.content.strip()
        if '</think>' in new_prompt:
            new_prompt = new_prompt.split('</think>')[-1].strip()
        return new_prompt
    except Exception as e:
        return None

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
    image_prompt = None
    if reply.startswith("IMAGE_REQUEST:"):
        lines = reply.split('\n', 1)
        image_prompt = lines[0].replace("IMAGE_REQUEST:", "").strip()
        reply = lines[1].strip() if len(lines) > 1 else "Image ban rahi hai..."
    return jsonify({"reply": reply, "image_prompt": image_prompt})

@app.route('/edit', methods=['POST'])
def edit():
    data = request.json
    image = data.get('image', '')
    instruction = data.get('instruction', 'enhance this image')
    new_prompt = analyze_and_edit(image, instruction)
    if new_prompt:
        return jsonify({"reply": "Lo yaar edited photo! 🎨", "image_prompt": new_prompt})
    else:
        return jsonify({"reply": "Masla aa gaya, dobara try karo.", "image_prompt": None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
