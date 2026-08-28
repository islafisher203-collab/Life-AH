from groq import Groq
from flask import Flask, request, jsonify, render_template_string
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
app = Flask(__name__)

SYSTEM = """You are Life-AH, an advanced AI assistant created by Abuzar.
Reply ONLY in the same language user writes in.
English only, Roman Urdu only, Urdu script only — match exactly.
NEVER use Hindi or Devanagari. Ever.
Be friendly, smart and helpful like a best friend."""

@app.route('/')
def home():
    return render_template_string("""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Life-AH</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0d0d0d;color:#fff;height:100vh;display:flex;flex-direction:column;overflow:hidden}
header{padding:16px 24px;background:linear-gradient(135deg,#1a1a2e,#16213e);border-bottom:1px solid #1e3a5f;display:flex;align-items:center;gap:14px;flex-shrink:0}
.logo{width:42px;height:42px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px}
.ht h1{font-size:20px;font-weight:700;background:linear-gradient(90deg,#667eea,#f093fb);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.ht p{font-size:12px;color:#667eea;margin-top:2px}
.st{margin-left:auto;display:flex;align-items:center;gap:6px;font-size:12px;color:#4ade80}
.dot{width:8px;height:8px;background:#4ade80;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px}
.msg{display:flex;gap:10px;animation:fi .3s ease}
@keyframes fi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.msg.user{flex-direction:row-reverse}
.av{width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.ai .av{background:linear-gradient(135deg,#667eea,#764ba2)}
.user .av{background:linear-gradient(135deg,#f093fb,#f5576c)}
.bbl{max-width:72%;padding:12px 16px;border-radius:16px;line-height:1.7;font-size:15px;word-break:break-word}
.ai .bbl{background:#1a1a2e;border:1px solid #2d2d5e;border-radius:4px 16px 16px 16px}
.user .bbl{background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px 4px 16px 16px}
.typ{background:#1a1a2e;border:1px solid #2d2d5e;border-radius:4px 16px 16px 16px;padding:14px 18px;display:flex;gap:5px;align-items:center}
.typ span{width:7px;height:7px;background:#667eea;border-radius:50%;animation:bc 1.2s infinite}
.typ span:nth-child(2){animation-delay:.2s}
.typ span:nth-child(3){animation-delay:.4s}
@keyframes bc{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-7px)}}
#bottom{padding:14px 20px;background:#111;border-top:1px solid #222;flex-shrink:0}
#box{display:flex;gap:10px;background:#1a1a1a;border:1px solid #333;border-radius:14px;padding:10px 14px;align-items:center}
#box:focus-within{border-color:#667eea}
#inp{flex:1;background:transparent;border:none;outline:none;color:#fff;font-size:15px;font-family:'Segoe UI',sans-serif}
#inp::placeholder{color:#444}
#btn{width:38px;height:38px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}
#btn svg{width:17px;height:17px;fill:white}
.wel{text-align:center;padding:50px 20px;color:#555}
.wel .ic{font-size:50px;margin-bottom:16px}
.wel h2{color:#667eea;margin-bottom:8px;font-size:22px}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-thumb{background:#222;border-radius:4px}
</style>
</head>
<body>
<header>
  <div class="logo">✨</div>
  <div class="ht"><h1>Life-AH</h1><p>Advanced AI Assistant by Abuzar</p></div>
  <div class="st"><div class="dot"></div>Online</div>
</header>
<div id="chat">
  <div class="wel">
    <div class="ic">✨</div>
    <h2>Welcome to Life-AH</h2>
    <p>Your intelligent AI companion<br>Ask anything in any language!</p>
  </div>
</div>
<div id="bottom">
  <div id="box">
    <input id="inp" type="text" placeholder="Ask me anything..." autocomplete="off">
    <button id="btn">
      <svg viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
    </button>
  </div>
</div>
<script>
var msgList = [];
var inp = document.getElementById('inp');
var btn = document.getElementById('btn');
var chatDiv = document.getElementById('chat');

function addBubble(text, role) {
  var d = document.createElement('div');
  d.className = 'msg ' + role;
  var a = document.createElement('div');
  a.className = 'av';
  a.textContent = role === 'ai' ? '✨' : '👤';
  var b = document.createElement('div');
  b.className = 'bbl';
  b.innerHTML = text.replace(/\n/g, '<br>');
  d.appendChild(a);
  d.appendChild(b);
  chatDiv.appendChild(d);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

function addTyping() {
  var d = document.createElement('div');
  d.className = 'msg ai';
  d.id = 'typDiv';
  var a = document.createElement('div');
  a.className = 'av';
  a.textContent = '✨';
  var t = document.createElement('div');
  t.className = 'typ';
  t.innerHTML = '<span></span><span></span><span></span>';
  d.appendChild(a);
  d.appendChild(t);
  chatDiv.appendChild(d);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

function removeTyping() {
  var t = document.getElementById('typDiv');
  if (t) t.remove();
}

function sendMessage() {
  var msg = inp.value.trim();
  if (!msg) return;
  var w = document.querySelector('.wel');
  if (w) w.remove();
  inp.value = '';
  addBubble(msg, 'user');
  addTyping();
  msgList.push({role: 'user', content: msg});
  fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({msgs: msgList})
  })
  .then(function(r) { return r.json(); })
  .then(function(d) {
    removeTyping();
    addBubble(d.reply, 'ai');
    msgList.push({role: 'assistant', content: d.reply});
    inp.focus();
  })
  .catch(function(e) {
    removeTyping();
    addBubble('Error: ' + e.message, 'ai');
  });
}

btn.addEventListener('click', sendMessage);
inp.addEventListener('keypress', function(e) {
  if (e.key === 'Enter') sendMessage();
});
inp.focus();
</script>
</body>
</html>""")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msgs = data.get('msgs', [])
    full = [{"role": "system", "content": SYSTEM}] + msgs
    r = client.chat.completions.create(model="openai/gpt-oss-20b", messages=full)
    return jsonify({"reply": r.choices[0].message.content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
