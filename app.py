from groq import Groq
from flask import Flask, request, jsonify, send_from_directory
import os
import urllib.parse
import base64
import random

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
app = Flask(__name__, static_folder='.')

SYSTEM = """You are Life-AH, a smart and friendly AI assistant created by Abuzar.

LANGUAGE RULES — VERY IMPORTANT:
- Most users write in Roman Urdu mixed with English — this is normal Pakistani style. Match it exactly.
- Example: if user writes "yar kya hal hai aaj" → reply in same Roman Urdu style
- Example: if user writes "bro what's up" → reply in English
- Example: if user writes in Urdu script → reply in Urdu script
- NEVER use Hindi (Devanagari script) — ever
- NEVER switch language unless user switches first
- Be casual, friendly, like a real Pakistani dost — use "yaar", "bhai", "achi baat" naturally

CAPABILITIES:
- Chat in any language or style
- Help with coding, writing, ideas, advice, facts
- Generate images when asked (use IMAGE_REQUEST format)
- Analyze and edit uploaded photos

IMAGE GENERATION — if user asks to draw/create/generate/make any image or photo:
Reply EXACTLY like this:
IMAGE_REQUEST: <detailed english description>
<friendly message in user's language>"""

def generate_image(prompt):
    seed = random.randint(1, 99999)
    encoded = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&seed={seed}&enhance=true"

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
                            "text": f"Describe this image in great detail. Then write a new image generation prompt that keeps ALL original details but applies this change: '{instruction}'. Output ONLY the prompt. No thinking, no explanation."
                        }
                    ]
                }
            ],
            max_tokens=400
        )
        new_prompt = response.choices[0].message.content.strip()
        if '</think>' in new_prompt:
            new_prompt = new_prompt.split('</think>')[-1].strip()
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
        friendly_msg = lines[1].strip() if len(lines) > 1 else "Image ban rahi hai..."
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
        reply = "Lo yaar, edited photo! 🎨"
    else:
        reply = f"Masla aa gaya: {prompt}"
    return jsonify({"reply": reply, "image_url": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
