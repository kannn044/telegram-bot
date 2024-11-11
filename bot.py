import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OLLAMA_URL = os.getenv('OLLAMA_URL')

conversation_history = {}

def query_ollama(user_id, prompt):
    conversation_history.setdefault(user_id, []).append({"role": "user", "content": prompt})

    json_payload = {
        "model": "gemma2:27b",
        "messages": conversation_history[user_id],
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=json_payload)
    if response.status_code == 200:
        result = response.json().get("message", {}).get("content", "")
        if result:
            conversation_history[user_id].append({"role": "assistant", "content": result})
            return result
        else:
            return "The AI returned an empty response."
    else:
        print("Error:", response.status_code, response.text)
        return "Sorry, I couldn't get a response from the AI."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text
    ai_response = query_ollama(user_id, user_message)

    await update.message.reply_text(ai_response)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    conversation_history[user_id] = []
    await update.message.reply_text("สวัสดีค่ะ! 😊 ยินดีที่ได้รู้จัก. คุณ มีอะไรให้ฉันช่วยไหมคะ?")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()