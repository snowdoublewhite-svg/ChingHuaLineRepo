import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai

app = Flask(__name__)

# 1. 自動讀取您在 Render 設定的密碼
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
genai.configure(api_key=GEMINI_API_KEY)

# 2. 自動讀取您在 Render 填寫的專業 Gem 指令
# 如果讀不到，它會使用後面的簡短文字當作備份
prompts = {
    "靈性諮詢": os.getenv('PROMPT_SPIRITUAL', "你是專業的九宮數靈性諮詢師。"),
    "命理占卜": os.getenv('PROMPT_FORTUNE', "你是精通命理占卜的大師。"),
    "健康分析": os.getenv('PROMPT_HEALTH', "你是專業的數字健康顧問。")
}

# 預設模式
current_mode = "靈性諮詢"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, filter_attribute=lambda e: isinstance(e.message, TextMessage))
def handle_message(event):
    global current_mode
    user_msg = event.message.text.strip()

    # 圖文選單按鈕的切換邏輯
    if "進入靈性諮詢" in user_msg:
        current_mode = "靈性諮詢"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔮 已切換至【靈性諮詢】模式"))
        return
    elif "進入命理占卜" in user_msg:
        current_mode = "命理占卜"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🗓️ 已切換至【命理占卜】模式"))
        return
    elif "進入健康分析" in user_msg:
        current_mode = "健康分析"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚖️ 已切換至【健康分析】模式"))
        return

    # 根據當前模式呼叫對應的 Gem 指令
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=prompts[current_mode])
        response = model.generate_content(user_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response.text))
    except Exception as e:
        print(f"Error: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="抱歉，我現在有點累了，請稍後再試。"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
