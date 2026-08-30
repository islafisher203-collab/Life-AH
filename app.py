from groq import Groq
from flask import Flask, request, jsonify, send_from_directory
import os
import random
import urllib.parse
import psycopg2
from datetime import datetime

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
DATABASE_URL = os.environ.get("DATABASE_URL", "")
app = Flask(__name__, static_folder='.')

def get_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id SERIAL PRIMARY KEY,
                session_id TEXT UNIQUE NOT NULL,
                title TEXT DEFAULT 'New Chat',
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("DB initialized!")
    except Exception as e:
        print(f"DB init error: {e}")

init_db()

SYSTEM = """Tu Life-AH hai — Abuzar ka banaya hua AI dost.

TU KAISE BAAT KARTA HAI:
- Tu bilkul ek Pakistani dost ki tarah baat karta hai
- Roman Urdu + English mix teri default style hai
- Emojis use kar naturally
- "yaar", "bhai", "achi baat", "haha", "sach mein?" aisa bolta hai
- Kabhi formal mat ban, kabhi robot jaisa mat baat kar
- User ki baat mein interest dikha, sawal pooch naturally

TU KIYA NAHI KARTA:
- Kabhi ChatGPT ya kisi aur AI ka naam NAHI leta
- Kabhi nahi kehta "main ek AI hoon" ya formal greeting
- Hindi KABHI NAHI

LANGUAGE:
- Roman Urdu → Roman Urdu
- English → English
- Urdu script → Urdu script

IMAGE BANANE KE LIYE:
IMAGE_REQUEST: <english description>
<friendly message>"""

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/new_chat', methods=['POST'])
def new_chat():
    try:
        session_id = 'chat_' + str(int(datetime.now().timestamp() * 1000))
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO chats (session_id, title) VALUES (%s, %s)", 
                   (session_id, 'New Chat'))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"session_id": session_id, "success": True})
    except Exception as e:
        print(f"new_chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_chats', methods=['GET'])
def get_chats():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT session_id, title, created_at FROM chats ORDER BY created_at DESC LIMIT 30")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        chats = [{"session_id": r[0], "title": r[1] or 'New Chat', "created_at": str(r[2])} for r in rows]
        return jsonify({"chats": chats})
    except Exception as e:
        print(f"get_chats error: {e}")
        return jsonify({"chats": []})

@app.route('/get_messages/<session_id>', methods=['GET'])
def get_messages(session_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT role, content FROM messages WHERE session_id = %s ORDER BY created_at ASC", 
                   (session_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        msgs = [{"role": r[0], "content": r[1]} for r in rows]
        return jsonify({"messages": msgs})
    except Exception as e:
        print(f"get_messages error: {e}")
        return jsonify({"messages": []})

@app.route('/delete_chat', methods=['POST'])
def delete_chat():
    try:
        session_id = request.json.get('session_id')
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM messages WHERE session_id = %s", (session_id,))
        cur.execute("DELETE FROM chats WHERE session_id = %s", (session_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msgs = data.get('msgs', [])
    session_id = data.get('session_id', '')
    user_msg = msgs[-1]['content'] if msgs else ''

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

    if session_id:
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
                       (session_id, 'user', user_msg))
            cur.execute("INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
                       (session_id, 'assistant', reply))
            title = user_msg[:40] if user_msg else 'New Chat'
            cur.execute("UPDATE chats SET title = %s WHERE session_id = %s",
                       (title, session_id))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"save msg error: {e}")

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
                {"type": "text", "text": f"Describe this image in detail then write a new image generation prompt applying: '{instruction}'. Output ONLY the prompt."}
            ]}],
            max_tokens=400
        )
        new_prompt = response.choices[0].message.content.strip()
        if '</think>' in new_prompt:
            new_prompt = new_prompt.split('</think>')[-1].strip()
        return jsonify({"reply": "Lo yaar edited photo! 🎨", "image_prompt": new_prompt})
    except Exception as e:
        return jsonify({"reply": "Masla aa gaya yaar 😅", "image_prompt": None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
