import os
import logging
import tempfile
from PIL import Image
import google.generativeai as genai

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
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# ENV KEYS (RAILWAY)
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing BOT_TOKEN or GEMINI_API_KEY")

# =========================
# GEMINI SETUP
# =========================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# MENU UI (VERSION 3)
# =========================
menu = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📊 Analyze Chart"), KeyboardButton("📈 Market Bias")],
        [KeyboardButton("💰 Risk Management"), KeyboardButton("🧠 SMC Guide")],
        [KeyboardButton("ℹ Help"), KeyboardButton("🔄 Restart Bot")]
    ],
    resize_keyboard=True
)

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Smart Money AI Bot v3\n\n"
        "Send a chart or use the menu below.",
        reply_markup=menu
    )

# =========================
# HELP
# =========================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 HOW TO USE:\n"
        "- Send chart screenshot 📸\n"
        "- Add caption like 'XAUUSD 15m'\n"
        "- Get full SMC breakdown\n\n"
        "⚠ Not financial advice"
    )

# =========================
# CHART ANALYSIS
# =========================
async def analyze_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
            path = tf.name

        await file.download_to_drive(path)
        image = Image.open(path)

        caption = update.message.caption or "Analyze this chart."

        prompt = f"""
You are a professional Smart Money Concept (SMC) trader.

Analyze the chart and give:

1. Trend direction
2. Market structure
3. Support & resistance
4. Liquidity sweep
5. BOS / CHOCH
6. Entry idea
7. Stop loss
8. Take profit
9. Confidence (0–100%)
10. Risk warning

User request:
{caption}

Rules:
- No profit guarantees
- Be realistic, not hype
"""

        response = model.generate_content([prompt, image])

        await update.message.reply_text(response.text)

        os.remove(path)

    except Exception as e:
        logging.error(e)
        await update.message.reply_text("❌ Chart analysis failed. Try again.")

# =========================
# MENU HANDLER
# =========================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 Analyze Chart":
        await update.message.reply_text("📸 Send a chart screenshot now.")
    
    elif text == "📈 Market Bias":
        await update.message.reply_text(
            "Send a pair like:\nXAUUSD / BTCUSD / EURUSD"
        )

    elif text == "💰 Risk Management":
        await update.message.reply_text(
            "💰 Risk Rules:\n"
            "- Risk 1–2% per trade\n"
            "- Always use SL\n"
            "- Avoid overtrading\n"
            "- No revenge trading"
        )

    elif text == "🧠 SMC Guide":
        await update.message.reply_text(
            "🧠 SMC Basics:\n"
            "- BOS = trend continuation\n"
            "- CHOCH = trend reversal\n"
            "- Liquidity = stop hunts\n"
            "- Order Blocks = key zones"
        )

    elif text == "🔄 Restart Bot":
        await start(update, context)

    else:
        await update.message.reply_text("Use the menu below 👇", reply_markup=menu)

# =========================
# PHOTO HANDLER
# =========================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await analyze_chart(update, context)

# =========================
# MAIN
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))

app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

print("🚀 Bot running...")

app.run_polling()
