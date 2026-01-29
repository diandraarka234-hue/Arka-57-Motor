import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from core import get_bot_reply

# =====================
# TOKEN BOT
# =====================
BOT_TOKEN = "8591611297:AAEwrWIo9_5CI-J8cBYDiwqYHiKWEUp4-08"

# =====================
# HANDLER PESAN
# =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = get_bot_reply(user_message)
    await update.message.reply_text(reply)

# =====================
# RUN BOT
# =====================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
