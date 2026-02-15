import json
import re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "7615544436:AAGhkg84m-nGyMxkqk072NGoUjtVwq8LFT0"
ADMIN_IDS = [7533465237]  # integer list
ORDER_LOG = "orders.json"
user_cooldown = {}

DIAMOND_PACKAGES = ["11","22","33","56","112","172","257","343","429","514",
                    "600","706","792","878","963","1049","1135","1412","2195",
                    "3688","5532","9288"]

PRICE_TEXT = """📢 Today Update Price 📢
💎 Weekly Pass
⭐️ TG Premium 1 Month – 20,000 Ks
Monthly Epic Bundle – 15,500 Ks
Weekly Elite Bundle – 3,100 Ks

💎 2x Recharge Event
Dia [50+50] – 3,200 Ks
Dia [150+150] – 9,300 Ks
Dia [250+250] – 14,900 Ks
Dia [500+500] – 29,900 Ks

Diamond Price:
💎 11 – 900 Ks
💎 22 – 1,700 Ks
💎 33 – 2,500 Ks
💎 56 – 4,000 Ks
💎 112 – 7,900 Ks
💎 172 – 9,500 Ks
💎 257 – 13,800 Ks
💎 343 – 18,600 Ks
💎 429 – 23,500 Ks
💎 514 – 27,500 Ks
💎 600 – 32,300 Ks
💎 706 – 37,500 Ks
💎 792 – 42,500 Ks
💎 878 – 46,200 Ks
💎 963 – 50,900 Ks
💎 1049 – 55,800 Ks
💎 1135 – 60,500 Ks
💎 1412 – 74,000 Ks
💎 2195 – 115,000 Ks
💎 3688 – 190,000 Ks
💎 5532 – 284,000 Ks
💎 9288 – 474,000 Ks

💬 Contact – @Ryo_h2
"""

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 Price List", callback_data="price")],
        [InlineKeyboardButton("📝 Order", callback_data="order")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ML Diamond Shop မှ ကြိုဆိုပါတယ် 🙏", reply_markup=reply_markup)

# Price callback
async def price_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(PRICE_TEXT)

# Order callback
async def order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    # Cooldown check
    now = datetime.now()
    last_time = user_cooldown.get(user_id)
    if last_time and now - last_time < timedelta(seconds=60):
        await query.edit_message_text("⏱ Please wait a bit before making another order.")
        return
    user_cooldown[user_id] = now

    context.user_data["step"] = "mlid"
    await query.edit_message_text("📝 ML ID + Server ပို့ပါ\nဥပမာ: 12345678 (1234)")

# Diamond selection callback
async def diamond_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("dia_"):
        dia = query.data.split("_")[1]
        context.user_data["amount"] = dia
        context.user_data["step"] = "payment"
        await query.edit_message_text(f"Selected {dia} Diamonds.\n💸 Payment screenshot ပို့ပါ")

# Text handler
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    text = update.message.text.strip()
    if step == "mlid":
        if not re.fullmatch(r"\d{7,10}", text):
            await update.message.reply_text("❌ Invalid ML ID.")
            return
        context.user_data["mlid"] = text
        context.user_data["step"] = "amount"
        
        # Diamond buttons
        keyboard = [
            [InlineKeyboardButton(dia, callback_data=f"dia_{dia}") for dia in DIAMOND_PACKAGES[i:i+4]] 
            for i in range(0, len(DIAMOND_PACKAGES), 4)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("💎 Diamond amount ကိုရွေးပါ:", reply_markup=reply_markup)

# Photo handler
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if step == "payment" and update.message.photo:
        data = context.user_data
        order = {
            "user": update.message.from_user.username,
            "mlid": data["mlid"],
            "amount": data["amount"],
            "timestamp": datetime.now().isoformat()
        }
        try:
            with open(ORDER_LOG, "r") as f:
                orders = json.load(f)
        except:
            orders = []
        orders.append(order)
        with open(ORDER_LOG, "w") as f:
            json.dump(orders, f, indent=2)

        for admin_id in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin_id,
                text=f"🆕 New Order\nML ID: {data['mlid']}\nAmount: {data['amount']}\nUser: @{update.message.from_user.username}")
            await context.bot.send_photo(chat_id=admin_id, photo=update.message.photo[-1].file_id)

        await update.message.reply_text("✅ Order လက်ခံပြီးပါပြီ")
        context.user_data.clear()

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(price_callback, pattern=r"^price$"))
    app.add_handler(CallbackQueryHandler(order_callback, pattern=r"^order$"))
    app.add_handler(CallbackQueryHandler(diamond_callback, pattern=r"^dia_"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    
    print("[DEBUG] Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()