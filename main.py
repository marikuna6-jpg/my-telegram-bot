import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("გამარჯობა! მე ვარ შენი AI ასისტენტი.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "meta-llama/llama-3.3-70b-instruct",
        "messages": [{"role": "user", "content": user_text}]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        res_json = response.json()
        
        if "choices" in res_json:
            bot_reply = res_json["choices"][0]["message"]["content"]
            await update.message.reply_text(bot_reply)
        else:
            await update.message.reply_text(f"ERR: {res_json}")
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"ERR: {str(e)}")

def main():
    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        print("ERROR: Tokens are missing!")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("ბოტი გაეშვა...")
    app.run_polling()

if __name__ == "__main__":
    main()
