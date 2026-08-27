from groq import Groq
import gradio as gr
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM = """You are Life-AH, a smart AI assistant made by Abuzar.
Reply ONLY in the same language user writes in.
- English → English only
- Roman Urdu → Roman Urdu only
- Urdu script → Urdu script only
- NEVER use Hindi or Devanagari. Ever.
Be friendly and fun like a best friend."""

def chat(message, history):
    msgs = [{"role": "system", "content": SYSTEM}]
    for h in history:
        msgs.append({"role": "user", "content": h[0]})
        msgs.append({"role": "assistant", "content": h[1]})
    msgs.append({"role": "user", "content": message})
    r = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs)
    return r.choices[0].message.content

gr.ChatInterface(fn=chat, title="Life-AH ✨", description="Your AI Friend!").launch(server_name="0.0.0.0", server_port=7860)
