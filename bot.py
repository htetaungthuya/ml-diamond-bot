# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ========== CONFIG ==========
TOKEN = "7615544436:AAGhkg84m-nGyMxkqk072NGoUjtVwq8LFT0"
ADMINS = [7533465237]  # သင့် admin ID

# Price list (example)
PRICES = {
    "Diamond11": 900,
    "Diamond22": 1700,
    "Diamond33": 2500,
    "Diamond56": 4000,
    "Diamond112": 7900,
}

# Store orders
ORDERS = {}

# ========== COMMANDS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 Price List", callback_data="price")],
        [InlineKeyboardButton("📦 My Orders", callback_data="myorders")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Save order
    ORDERS[user_id] = text

    # Notify admins
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"New order from {update.message.from_user.username or user_id}:\n{text}\nConfirm: /confirm {user_id}  Cancel: /cancel {user_id}"
            )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

    await update.message.reply_text("Your order has been received!")

# ========== INLINE BUTTONS ==========
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(cache_time=5)  # Timeout fix

    if query.data == "price":
        price_text = "\n".join([f"{k}: {v} ks" for k, v in PRICES.items()])
        await query.message.reply_text(f"💎 Current Prices:\n{price_text}")
    elif query.data == "myorders":
        user_orders = ORDERS.get(query.from_user.id)
        if user_orders:
            await query.message.reply_text(f"Your orders:\n{user_orders}")
        else:
            await query.message.reply_text("You have no orders yet.")

# ========== ADMIN COMMANDS ==========
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        await update.message.reply_text("You are not authorized.")
        return
    try:
        user_id = int(context.args[0])
        if user_id in ORDERS:
            await update.message.reply_text(f"Order from {user_id} confirmed.")
            del ORDERS[user_id]
        else:
            await update.message.reply_text("No order found for this user.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMINS:
        await update.message.reply_text("You are not authorized.")
        return
    try:
        user_id = int(context.args[0])
        if user_id in ORDERS:
            await update.message.reply_text(f"Order from {user_id} canceled.")
            del ORDERS[user_id]
        else:
            await update.message.reply_text("No order found for this user.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# ========== APPLICATION ==========
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("confirm", confirm))
app.add_handler(CommandHandler("cancel", cancel))

print("Bot is running...")
app.run_polling()