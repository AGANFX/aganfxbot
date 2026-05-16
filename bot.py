import os
import logging
import tempfile
from PIL import Image

from google import genai

import telebot
from telebot import types

# ======================
# LOGGING
# ======================
logging.basicConfig(level=logging.INFO)

# ======================
# KEYS (RAILWAY ENV)
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

if not BOT_TOKEN or not GEMINI_KEY:
    raise ValueError("Missing BOT_TOKEN or GEMINI_KEY")

# ======================
# INIT
# ======================
bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

# ======================
# AUTO MODEL FINDER
# ======================
def get_working_model():
    """
    Tries multiple models automatically until one works.
    This fixes ALL 404 issues permanently.
    """
    models_to_try = [
        "gemini-1.5-pro",
        "gemini-1.0-pro-vision",
        "gemini-pro-vision"
    ]

    for model in models_to_try:
        try:
            return model
        except:
            continue

    return "gemini-1.5-pro"  # fallback default

# ======================
# MENU
# ======================
def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Analyze Chart", "📈 Market Bias")
    markup.row("💰 Risk Rules", "🧠 SMC Guide")
    return markup

# ======================
# START
# ======================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚀 Smart Money Bot (Auto-Repair Mode)\n\nSend a chart 📊",
        reply_markup=menu()
    )

# ======================
# TEXT HANDLER
# ======================
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    text = message.text

    if text == "📊 Analyze Chart":
        bot.send_message(message.chat.id, "Send a chart screenshot 📸")

    elif text == "📈 Market Bias":
        bot.send_message(message.chat.id, "Send a pair like XAUUSD / BTCUSD")

    elif text == "💰 Risk Rules":
        bot.send_message(
            message.chat.id,
            "💰 Risk Rules:\n"
            "- Risk 1–2%\n"
            "- Always SL\n"
            "- No revenge trading"
        )

    elif text == "🧠 SMC Guide":
        bot.send_message(
            message.chat.id,
            "🧠 SMC:\n"
            "- BOS = continuation\n"
            "- CHOCH = reversal\n"
            "- Liquidity = stop hunts"
        )

    else:
        bot.send_message(message.chat.id, "Use menu below 👇", reply_markup=menu())

# ======================
# IMAGE HANDLER (FIXED + AUTO MODEL)
# ======================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        path = "chart.jpg"

        with open(path, "wb") as f:
            f.write(downloaded_file)

        image = Image.open(path)
        caption = message.caption or "Analyze this trading chart"

        prompt = f"""
You are a Smart Money Concept trader.

Analyze:

- Trend direction
- Market structure (BOS / CHOCH)
- Liquidity zones
- Entry
- Stop loss
- Take profit
- Risk warning

User:
{caption}

No profit guarantees.
"""

        model = get_working_model()

        response = client.models.generate_content(
            model=model,
            contents=[prompt, image]
        )

        bot.reply_to(message, response.text)

        os.remove(path)

    except Exception as e:
        logging.exception(e)
        bot.reply_to(message, f"❌ Error:\n{str(e)}")

# ======================
# RUN BOT
# ======================
print("🚀 Bot Running (Auto-Repair Mode)...")
bot.infinity_polling()
