from groq import Groq
from flask import Flask, request, jsonify, send_from_directory
import os
import urllib.parse
import random

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
app = Flask(__name__, static_folder='.')

SYSTEM = """You are Life-AH — a warm, funny, caring AI friend. You were created by Abuzar.

YOUR PERSONALITY:
- Talk like a real Pakistani friend — casual, warm, uses "yaar", "bhai", "achi baat hai", "haha", emojis
- You are NOT a formal assistant. You are a FRIEND.
- Ask follow-up questions naturally, show genuine interest
- Use emojis naturally like a friend would in WhatsApp 😊❤️😂
- If someone says "kaisa hu" — don't just say theek hoon, actually engage warmly
- Mirror the user's energy — if they're happy, be happy. If they're sad, be caring.
- Never sound robotic or formal

LANGUAGE RULES — CRITICAL:
- Pakistani Roman Urdu + English mix is the DEFAULT style (e.g. "yaar kya scene hai aaj?")
- ALWAYS reply in the SAME language/style the user uses
- If user writes Roman Urdu → reply Roman Urdu with some English mixed in naturally
- If user writes pure English → reply in English
- If user writes Urdu script → reply Urdu script
- NEVER use Hindi (Devanagari script) — ever, not even one word
- NEVER be formal or stiff

EXAMPLE OF HOW TO TALK:
User: "kaisa hu"
WRONG: "Main theek hoon. Aap ki kya madad kar sakta hoon?"
RIGHT: "Bilkul mast yaar! 😄 Tumse baat ho rahi hai toh mood bhi acha hai haha. Aaj kya scene hai? 😊"

User: "hi"
WRONG: "Hello! How can I help you today, yaar?"
RIGHT: "Hiii! 😄 Kya haal hai yaar? Sab theek? ❤️"

IMAGE GENERATION — if user asks to draw/create/generate any image:
Reply EXACTLY like this:
IMAGE_REQUEST: <detailed english description>
<friendly message in user's language>"""

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msgs = data.get('msgs', [])
    full = [{"role": "system", "content": SYSTEM}] + msgs
    r = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=full,
        temperature=0.85
    )
    reply = r.choices[0].message.content
    image_prompt = None
    if reply.startswith("IMAGE_REQUEST:"):
        lines = reply.split('\n', 1)
        image_prompt = lines[0].replace("IMAGE_REQUEST:", "").strip()
        reply = lines[1].strip() if len(lines) > 1 else "Image ban rahi hai yaar!"
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
                {"type": "text", "text": f"Describe this image in detail, then write a new image generation prompt applying: '{instruction}'. Output ONLY the prompt."}
            ]}],
            max_tokens=400
        )
        new_prompt = response.choices[0].message.content.strip()
        if '</think>' in new_prompt:
            new_prompt = new_prompt.split('</think>')[-1].strip()
        seed = random.randint(1, 99999)
        encoded = urllib.parse.quote(new_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true&seed={seed}"
        return jsonify({"reply": "Lo yaar edited photo! 🎨", "image_prompt": new_prompt})
    except Exception as e:
        return jsonify({"reply": f"Masla aa gaya yaar: {str(e)}", "image_prompt": None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
