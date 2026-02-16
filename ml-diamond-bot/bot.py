import asyncio
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

BOT_TOKEN = "7615544436:AAGhkg84m-nGyMxkqk072NGoUjtVwq8LFT0"

PROMO_TEXT = """
🔥 ML DIAMOND PROMO 🔥

💎 Diamond top-up
⚡ Fast & Safe
📩 Order now!

👉 Contact Admin
"""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Online (VC Promo Active)")

async def vc_started(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"🎧 VC started in {chat_id}")

    await asyncio.sleep(30)

    await context.bot.send_message(
        chat_id=chat_id,
        text=PROMO_TEXT
    )

    print("📢 Promo sent")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.StatusUpdate.VIDEO_CHAT_STARTED, vc_started)
    )

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
