from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('YOUR_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('YOUR_CHANNEL_SECRET'))
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def generate_response(prompt, role="user"):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一個很有用處的幫手"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.lower()
    if msg.startswith('/echo ') :
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg[6:]))
    elif msg.startswith('/g '):
        response = generate_response(msg[3:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response))
    elif msg.startswith('/t '):
        response = generate_response("請幫我翻譯正體中文:"+msg[3:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response))
    elif msg.startswith('/e '):
        response = generate_response("請幫我翻譯英文:"+msg[3:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response))
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text)
    # )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)