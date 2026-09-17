import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# 1. Flask ვებ-სერვერი Render-ის პორტისთვის
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

# 2. ლოგირების კონფიგურაცია
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 3. გარემო ცვლადების მიღება
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Groq კლიენტის ინიციალიზაცია
groq_client = Groq(api_key=GROQ_API_KEY)

# 4. Telegram ბოტის ჰენდლერები
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("გამარჯობა! მე ვარ შენი AI ასისტენტი. მოგწერე ნებისმიერი კითხვა!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama3-8b-8192",
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("შეცდომა მოხდა პასუხის გენერირებისას.")

# 5. ბოტის გაშვება
def main():
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        print("ERROR: TELEGRAM_TOKEN or GROQ_API_KEY is missing!")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("ბოტი წარმატებით გაეშვა...")
    application.run_polling()

if __name__ == "__main__":
    main()
