import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai

app = Flask(__name__)

# --- 【填空 A：填入你的密碼】 ---
line_bot_api = LineBotApi('這裡貼上你的 LINE_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('這裡貼上你的 LINE_CHANNEL_SECRET')
genai.configure(api_key="這裡貼上你的 GEMINI_API_KEY")

# --- 【填空 B：貼上你的三個 Gem 指令】 ---
GEMS_CONFIG = {
    "spiritual": '''這裡貼上【靈性諮詢】的 Gem 指令內容''',
    "divination": '''這裡貼上【命理占卜】的 Gem 指令內容''',
    "health": '''這裡貼上【健康分析】的 Gem 指令內容'''
}

user_sessions = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_msg = event.message.text.strip()

    # 切換大腦的關鍵字
    if user_msg == "進入靈性諮詢":
        user_sessions[user_id] = "spiritual"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔮 已切換至【靈性諮詢】模式"))
        return
    elif user_msg == "進入命理占卜":
        user_sessions[user_id] = "divination"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🗓️ 已切換至【命理占卜】模式"))
        return
    elif user_msg == "進入健康分析":
        user_sessions[user_id] = "health"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚖️ 已切換至【健康分析】模式"))
        return

    # 沒選過的話預設用靈性諮詢
    current_mode = user_sessions.get(user_id, "spiritual")
    my_instruction = GEMS_CONFIG[current_mode]

    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=my_instruction)
    response = model.generate_content(user_msg)

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response.text))

if __name__ == "__main__":
    app.run()
