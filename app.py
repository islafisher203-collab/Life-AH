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
    r = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=msgs
    )
    reply = r.choices[0].message.content
    history = history + [[message, reply]]
    return "", history

with gr.Blocks(title="Life-AH") as demo:
    gr.Markdown("# Life-AH ✨\nYour AI Friend!")
    chatbot = gr.Chatbot(height=500)
    with gr.Row():
        txt = gr.Textbox(placeholder="Kuch bhi likho...", scale=4, show_label=False)
        btn = gr.Button("Send ➤", scale=1, variant="primary")
    btn.click(chat, [txt, chatbot], [txt, chatbot])
    txt.submit(chat, [txt, chatbot], [txt, chatbot])

demo.launch(server_name="0.0.0.0", server_port=7860)
