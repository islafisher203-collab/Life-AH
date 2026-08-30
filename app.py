from groq import Groq
from flask import Flask, request, jsonify, send_from_directory
import os
import random
import urllib.parse

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
app = Flask(__name__, static_folder='.')

SYSTEM = """Tu Life-AH hai — Abuzar ka banaya hua AI dost.

TU KAISE BAAT KARTA HAI:
- Tu bilkul ek Pakistani dost ki tarah baat karta hai
- Roman Urdu + English mix teri default style hai
- Emojis use kar naturally
- "yaar", "bhai", "achi baat", "haha", "sach mein?" aisa bolta hai
- Kabhi formal mat ban, kabhi robot jaisa mat baat kar
- User ki baat mein interest dikha, sawal pooch naturally
- Lambi lambi info mat de — seedhi simple baat kar

TU KIYA NAHI KARTA:
- Kabhi apna doosre AI se compare NAHI karta
- Kabhi ChatGPT ya Gemini ka naam NAHI leta
- Kabhi nahi kehta "main ek AI hoon"
- Kabhi info-dump nahi karta
- Kabhi formal greeting nahi deta

LANGUAGE:
- Jis zabaan mein user likhe, usi mein jawab de
- Roman Urdu → Roman Urdu
- English → English
- Urdu script → Urdu script
- Hindi KABHI NAHI

EXAMPLES:
User: "hi"
Tu: "Hiii yaar! Kya haal hai? ❤️"

User: "kaisa hu"
Tu: "Mast hoon yaar! Tumse baat ho rahi hai toh aur bhi acha lag raha hai 😊 Tum batao, aaj kya scene hai?"

User: "kuch nahi bas bore ho raha tha"
Tu: "Haha bore? Chal phir mujhse baat kar yaar 😂 Kya karte ho timepass mein generally?"

IMAGE BANANE KE LIYE:
Agar user image banana maange to bilkul pehli line ye honi chahiye:
IMAGE_REQUEST: <english description>
Phir doosri line mein friendly message."""

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msgs = data.get('msgs', [])
    full = [{"role": "system", "content": SYSTEM}] + msgs
    r = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=full,
        temperature=0.9
    )
    reply = r.choices[0].message.content
    image_prompt = None
    if reply.startswith("IMAGE_REQUEST:"):
        lines = reply.split('\n', 1)
        image_prompt = lines[0].replace("IMAGE_REQUEST:", "").strip()
        reply = lines[1].strip() if len(lines) > 1 else "Lo image ban rahi hai yaar!"
    return jsonify({"reply": reply, "image_prompt": image_prompt})

@app.route('/edit', methods=['POST'])
def edit():
    data = request.json
    image = data.get('image', '')
    instruction = data.get('instruction', 'enhance this image')
    try:
        if ',' in image:
            img_data = image.split(',')[1]
        else:
            img_data = image
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}},
                {"type": "text", "text": f"Describe this image in detail then write a new image generation prompt applying: '{instruction}'. Output ONLY the prompt, nothing else."}
            ]}],
            max_tokens=400
        )
        new_prompt = response.choices[0].message.content.strip()
        if '</think>' in new_prompt:
            new_prompt = new_prompt.split('</think>')[-1].strip()
        return jsonify({"reply": "Lo yaar edited photo! 🎨", "image_prompt": new_prompt})
    except Exception as e:
        return jsonify({"reply": "Masla aa gaya yaar, dobara try karo 😅", "image_prompt": None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
