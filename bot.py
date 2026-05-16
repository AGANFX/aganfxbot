import os
import logging
import tempfile
from PIL import Image

from google import genai

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
# ENV KEYS
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing BOT_TOKEN or GEMINI_API_KEY")

# =========================
# GEMINI (NEW SDK)
# =========================
client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# MENU UI
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
        "🚀 Smart Money Bot (Railway Ready)\n\nSend a chart image or use menu.",
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
        "- Get SMC analysis"
    )

# =========================
# CHART ANALYSIS (GEMINI)
# =========================
async def analyze_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
            path = tf.name

        await file.download_to_drive(path)

        image = Image.open(path)
        caption = update.message.caption or "Analyze this trading chart."

        prompt = f"""
You are a Smart Money Concept (SMC) trading analyst.

Analyze the chart:

1. Trend direction
2. Market structure
3. BOS / CHOCH
4. Liquidity sweep
5. Support & resistance
6. Entry idea
7. Stop loss
8. Take profit
9. Confidence (0-100%)
10. Risk warning

User request:
{caption}

Rules:
- No guaranteed profits
- Be realistic
"""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, image]
        )

        await update.message.reply_text(response.text)

        os.remove(path)

    except Exception as e:
        logging.error(e)
        await update.message.reply_text("❌ Error analyzing chart.")

# =========================
# MENU HANDLER
# =========================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 Analyze Chart":
        await update.message.reply_text("Send a chart image now 📸")

    elif text == "📈 Market Bias":
        await update.message.reply_text("Send symbol: XAUUSD / BTCUSD / EURUSD")

    elif text == "💰 Risk Rules":
        await update.message.reply_text(
            "💰 Risk Rules:\n"
            "- Risk 1–2% per trade\n"
            "- Always use Stop Loss\n"
            "- Avoid overtrading\n"
            "- Wait for BOS/CHOCH confirmation"
        )

    elif text == "🧠 SMC Guide":
        await update.message.reply_text(
            "🧠 SMC Basics:\n"
            "- BOS = trend continuation\n"
            "- CHOCH = reversal\n"
            "- Liquidity = stop hunts\n"
            "- Order blocks = entry zones"
        )

    else:
        await update.message.reply_text("Use the menu below 👇", reply_markup=menu)

# =========================
# PHOTO HANDLER
# =========================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await analyze_chart(update, context)

# =========================
# MAIN APP
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))

app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

print("🚀 Bot Running...")
app.run_polling()
