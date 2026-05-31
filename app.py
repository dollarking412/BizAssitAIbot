import os
import logging
import google.generativeai as genai
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, filters

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Get your FREE key from https://aistudio.google.com/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')  # free & fast

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

def get_ai_reply(user_message: str) -> str:
    try:
        response = model.generate_content(
            f"You are BizAssist AI, a professional customer support chatbot for businesses. "
            f"Keep replies short and helpful. User: {user_message}"
        )
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Sorry, error: {str(e)}"

async def handle_message(update, context):
    user_msg = update.message.text
    reply = get_ai_reply(user_msg)
    await update.message.reply_text(reply)

dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return 'ok', 200
    except Exception as e:
        logging.error(f"Error: {e}")
        return 'error', 500

@app.route('/')
def home():
    return "BizAssist AI is running with Gemini (free) ✅"

if __name__ == '__main__':
    bot.set_webhook(WEBHOOK_URL)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
