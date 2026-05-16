import os
import logging
import tempfile
from PIL import Image

import google.genai as genai

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# KEYS
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing BOT_TOKEN or GEMINI_API_KEY")

# =========================
# GEMINI
# =========================
client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# MENU
# =========================
menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📊 Analyze Chart"), KeyboardButton("📈 Market Bias")],
        [KeyboardButton("💰 Risk Rules"), KeyboardButton("🧠 SMC Guide")],
        [KeyboardButton("ℹ Help")]
    ],
    resize_keyboard=True
)

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Smart Money Bot Ready\nSend chart screenshot 📸",
        reply_markup=menu
    )

# =========================
# HELP
# =========================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Send a chart screenshot with caption like 'XAUUSD 15m'"
    )

# =========================
# CHART ANALYSIS (FULLY FIXED)
# =========================
async def analyze_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
            path = tf.name

        await file.download_to_drive(path)

        caption = update.message.caption or "Analyze this chart."

        prompt = f"""
You are a Smart Money Concept trader.

Give:
1. Trend
2. Market structure
3. BOS / CHOCH
4. Liquidity
5. Entry
6. SL
7. TP
8. Confidence %
9. Risk warning

User:
{caption}
"""

        # OPEN IMAGE SAFELY
        with open(path, "rb") as f:
            image_bytes = f.read()

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                }
            ]
        )

        await update.message.reply_text(response.text)

        os.remove(path)

    except Exception as e:
        logging.exception("BOT ERROR")
        await update.message.reply_text(
            "❌ Bot error occurred.\n\n"
            "Reason:\n"
            f"{str(e)}"
        )

# =========================
# MENU HANDLER
# =========================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 Analyze Chart":
        await update.message.reply_text("Send a chart screenshot 📸")

    elif text == "📈 Market Bias":
        await update.message.reply_text("Send symbol: XAUUSD / BTCUSD")

    elif text == "💰 Risk Rules":
        await update.message.reply_text(
            "💰 Risk:\n- 1–2% risk\n- Always SL\n- Wait BOS/CHOCH"
        )

    elif text == "🧠 SMC Guide":
        await update.message.reply_text(
            "SMC:\nBOS = continuation\nCHOCH = reversal\nLiquidity = stop hunts"
        )

    else:
        await update.message.reply_text("Use menu 👇", reply_markup=menu)

# =========================
# APP
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(MessageHandler(filters.PHOTO, analyze_chart))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

print("🚀 Bot Running...")
app.run_polling()
