import telebot
from telebot import types
import requests
import base64
import os
from PIL import Image
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing")

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# START MENU
# =========================
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(
        types.KeyboardButton("📊 Analyze Chart"),
        types.KeyboardButton("📚 Guide")
    )

    bot.send_message(
        message.chat.id,
        f"""
🔥 AMUDANCE FX AI PRO ENGINE 🔥

Welcome {message.from_user.first_name}

📸 Send a chart screenshot
🧠 AI will analyze market structure
📊 No random signals

Ready.
""",
        reply_markup=markup
    )

# =========================
# GUIDE
# =========================
@bot.message_handler(func=lambda m: m.text == "📚 Guide")
def guide(m):
    bot.send_message(
        m.chat.id,
        """
📊 HOW TO USE

1. Send MT5 / TradingView screenshot
2. Wait for AI analysis
3. Get:
   - Trend direction
   - Structure
   - Entry zone
   - SL / TP
   - Confidence
"""
    )

# =========================
# IMAGE HANDLER (REAL AI CORE)
# =========================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    loading = bot.send_message(message.chat.id, "🧠 AI analyzing chart...")

    try:
        # download image
        file_info = bot.get_file(message.photo[-1].file_id)
        file = bot.download_file(file_info.file_path)

        path = "chart.jpg"
        with open(path, "wb") as f:
            f.write(file)

        # compress
        img = Image.open(path)
        img.save(path, optimize=True, quality=60)

        # convert to base64
        with open(path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        # =========================
        # REAL AI ANALYSIS PROMPT
        # =========================
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-4.1-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
You are a professional Smart Money Concept trader.

Analyze this chart and give:

1. Market Trend (Bullish / Bearish / Range)
2. Market Structure (BOS / CHoCH if visible)
3. Liquidity zones
4. Best entry zone
5. Stop loss level
6. Take profit levels (1:2 minimum RR)
7. Confidence score (0-100%)
8. Short reasoning

IMPORTANT:
- Do NOT repeat templates
- Every chart must be unique analysis
- Be precise like institutional trader
"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}"
                            }
                        }
                    ]
                }
            ]
        }

        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90
        )

        data = r.json()

        if "choices" not in data:
            raise Exception(str(data))

        result = data["choices"][0]["message"]["content"]

        final = f"""
🔥 AMUDANCE FX AI SIGNAL 🔥

{result}

━━━━━━━━━━━━━━━
⚡ AI Vision Engine Active
🧠 No Random Logic
📊 Real Chart Interpretation
"""

        bot.edit_message_text(
            final,
            message.chat.id,
            loading.message_id
        )

    except Exception as e:
        bot.edit_message_text(
            f"❌ AI Error:\n{e}",
            message.chat.id,
            loading.message_id
        )

# =========================
# RUN BOT
# =========================
print("AMUDANCE FX AI VISION ENGINE RUNNING...")
bot.infinity_polling(timeout=30, long_polling_timeout=30)
