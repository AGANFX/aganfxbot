import telebot
from telebot import types
from PIL import Image
from google import genai
import os

# ======================
# KEYS (USE ENV ON RAILWAY)
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
# MENU
# ======================
def main_menu():
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
        "🚀 Smart Money Bot Ready\n\nSend a chart screenshot 📊",
        reply_markup=main_menu()
    )

# ======================
# MENU HANDLER
# ======================
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):

    text = message.text

    if text == "📊 Analyze Chart":
        bot.send_message(message.chat.id, "📸 Send a chart screenshot now")

    elif text == "📈 Market Bias":
        bot.send_message(message.chat.id, "Send a symbol like XAUUSD or BTCUSD")

    elif text == "💰 Risk Rules":
        bot.send_message(
            message.chat.id,
            "💰 Risk Rules:\n"
            "- Risk 1–2%\n"
            "- Always SL\n"
            "- Avoid overtrading"
        )

    elif text == "🧠 SMC Guide":
        bot.send_message(
            message.chat.id,
            "🧠 SMC Basics:\n"
            "- BOS = continuation\n"
            "- CHOCH = reversal\n"
            "- Liquidity = stop hunts"
        )

    else:
        bot.send_message(message.chat.id, "Use the menu 👇", reply_markup=main_menu())

# ======================
# IMAGE HANDLER
# ======================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        image_path = "chart.jpg"

        with open(image_path, "wb") as f:
            f.write(downloaded_file)

        image = Image.open(image_path)

        caption = message.caption or "Analyze this trading chart"

        prompt = f"""
You are a Smart Money Concept (SMC) trading analyst.

Analyze the chart:

- Trend direction
- Market structure (BOS / CHOCH)
- Liquidity zones
- Entry point
- Stop loss
- Take profit
- Risk warning

User request:
{caption}

Do NOT guarantee profits.
"""

        # FIXED MODEL NAME (important)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, image]
        )

        bot.reply_to(message, response.text)

    except Exception as e:
        bot.reply_to(message, f"❌ Error:\n{str(e)}")

# ======================
# RUN BOT
# ======================
print("🚀 Bot is running...")
bot.infinity_polling()
