from groq import Groq
from flask import Flask, request, jsonify, render_template_string
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])
app = Flask(__name__)

SYSTEM = """You are Life-AH, an advanced AI assistant created by Abuzar.
Reply ONLY in the same language user writes in.
- English → English only
- Roman Urdu → Roman Urdu only
- Urdu script → Urdu script only
- NEVER use Hindi or Devanagari. Ever.
Be friendly, smart and helpful like a best friend."""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Life-AH</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0d0d0d;color:#fff;height:100vh;display:flex;flex-direction:column}
header{padding:16px 24px;background:linear-gradient(135deg,#1a1a2e,#16213e);border-bottom:1px solid #1e3a5f;display:flex;align-items:center;gap:14px}
.logo{width:42px;height:42px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 4px 15px rgba(102,126,234,0.4)}
.header-text h1{font-size:20px;font-weight:700;background:linear-gradient(90deg,#667eea,#764ba2,#f093fb);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.header-text p{font-size:12px;color:#667eea;margin-top:2px}
.status{margin-left:auto;display:flex;align-items:center;gap:6px;font-size:12px;color:#4ade80}
.dot{width:8px;height:8px;background:#4ade80;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(1.2)}}
#chat{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:20px}
.msg{display:flex;gap:12px;animation:fadeIn .3s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.msg.user{flex-direction:row-reverse}
.avatar{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.ai-av{background:linear-gradient(135deg,#667eea,#764ba2)}
.user-av{background:linear-gradient(135deg,#f093fb,#f5576c)}
.bubble{max-width:70%;padding:14px 18px;border-radius:16px;line-height:1.7;font-size:15px}
.ai .bubble{background:#1a1a2e;border:1px solid #2d2d5e;border-radius:4px 16px 16px 16px}
.user .bubble{background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px 4px 16px 16px}
.typing-bubble{background:#1a1a2e;border:1px solid #2d2d5e;border-radius:4px 16px 16px 16px;padding:14px 18px}
.typing{display:flex;gap:5px;align-items:center}
.typing span{width:8px;height:8px;background:#667eea;border-radius:50%;animation:bounce 1.2s infinite}
.typing span:nth-child(2){animation-delay:.2s}
.typing span:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-8px)}}
#bottom{padding:16px 24px;background:#111;border-top:1px solid #1e1e1e}
#inputbox{display:flex;gap:10px;background:#1a1a1a;border:1px solid #2d2d2d;border-radius:16px;padding:12px 16px;align-items:flex-end;transition:border .2s}
#inputbox:focus-within{border-color:#667eea}
textarea{flex:1;background:transparent;border:none;outline:none;color:#fff;font-size:15px;resize:none;max-height:120px;font-family:'Segoe UI',sans-serif;line-height:1.5}
textarea::placeholder{color:#444}
#send{width:40px;height:40px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:transform .2s}
#send:hover{transform:scale(1.05)}
#send svg{width:18px;height:18px;fill:white}
.welcome{text-align:center;padding:40px 20px;color:#444}
.welcome .icon{font-size:48px;margin-bottom:16px}
.welcome h2{font-size:22px;color:#667eea;margin-bottom:8px}
.welcome p{font-size:14px;line-height:1.6}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-thumb{background:#2d2d2d;border-radius:4px}
</style>
</head>
<body>
<header>
  <div class="logo">✨</div>
  <div class="header-text">
    <h1>Life-AH</h1>
    <p>Advanced AI Assistant by Abuzar</p>
  </div>
  <div class="status"><div class="dot"></div>Online</div>
</header>
<div id="chat">
  <div class="welcome">
    <div class="icon">✨</div>
    <h2>Welcome to Life-AH</h2>
    <p>Your intelligent AI companion.<br>Ask me anything in any language!</p>
  </div>
</div>
<div id="bottom">
  <div id="inputbox">
    <textarea id="inp" rows="1" placeholder="Ask me anything..."></textarea>
    <button id="send" onclick="send()">
      <svg viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
    </button>
  </div>
</div>
<script>
const chat=document.getElementById('chat'),inp=document.getElementById('inp');
let history=[];
function addMsg(text,role){
  const d=document.createElement('div');
  d.className='msg '+(role==='ai'?'ai':'user');
  const av=document.createElement('div');
  av.className='avatar '+(role==='ai'?'ai-av':'user-av');
  av.textContent=role==='ai'?'✨':'👤';
  const b=document.createElement('div');
  b.className='bubble';
  b.innerHTML=text.replace(/\n/g,'<br>');
  d.appendChild(av);d.appendChild(b);
  chat.appendChild(d);
  chat.scrollTop=chat.scrollHeight;
}
function showTyping(){
  const d=document.createElement('div');
  d.className='msg ai';d.id='typing';
  d.innerHTML='<div class="avatar ai-av">✨</div><div class="typing-bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
  chat.appendChild(d);chat.scrollTop=chat.scrollHeight;
}
async function send(){
  const msg=inp.value.trim();
  if(!msg)return;
  const welcome=document.querySelector('.welcome');
  if(welcome)welcome.remove();
  inp.value='';
  inp.style.height='auto';
  addMsg(msg,'user');
  showTyping();
  history.push({role:'user',content:msg});
  try{
    const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({history:history})});
    const data=await r.json();
    document.getElementById('typing')?.remove();
    addMsg(data.reply,'ai');
    history.push({role:'assistant',content:data.reply});
  }catch(e){
    document.getElementById('typing')?.remove();
    addMsg('Connection error. Please try again.','ai');
  }
}
inp.addEventListener('keydown',function(e){
  if(e.key==='Enter'&&!e.shiftKey){
    e.preventDefault();
    send();
  }
});
inp.addEventListener('input',function(){
  this.style.height='auto';
  this.style.height=this.scrollHeight+'px';
});
</script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    history = data.get('history', [])
    msgs = [{"role": "system", "content": SYSTEM}] + history
    r = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=msgs
    )
    return jsonify({"reply": r.choices[0].message.content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, threaded=True)
