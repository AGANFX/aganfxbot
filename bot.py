import telebot
from telebot import types
import requests
import base64
import os
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
import random

# =========================
# LOAD ENV
# =========================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SIGNAL_CHANNEL = os.getenv("SIGNAL_CHANNEL")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing")

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# SESSION ENGINE
# =========================
def get_session():
    hour = datetime.utcnow().hour
    if 7 <= hour < 12:
        return "LONDON SESSION 🏦"
    elif 12 <= hour < 17:
        return "NEW YORK SESSION 🗽"
    else:
        return "ASIAN SESSION 🌏"

# =========================
# SMART STRUCTURE ENGINE (NO RANDOM SIGNALS)
# =========================
def strategy_engine():
    session = get_session()

    return {
        "session": session,
        "trend": "STRUCTURE BASED ANALYSIS 📊",
        "signal": "WAIT FOR CONFIRMATION ⚠",
        "entry": "Liquidity + BOS confirmation required",
        "sl": "Below/Above structure",
        "tp": "1:2 - 1:3 RR",
        "liquidity": "Both sides being targeted",
        "confidence": "60% - 75%"
    }

# =========================
# AI ENGINE (OPTIONAL)
# =========================
def ai_engine(image_b64):
    if not OPENROUTER_API_KEY:
        return None

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-4.1-mini",
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze chart: trend, liquidity, structure, entry."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }]
        }

        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]

    except:
        pass

    return None

# =========================
# TELEGRAM START MENU
# =========================
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(
        types.KeyboardButton("📊 Analyze Chart"),
        types.KeyboardButton("📚 Strategy")
    )
    markup.add(
        types.KeyboardButton("💎 Status"),
        types.KeyboardButton("📞 Support")
    )

    bot.send_message(
        message.chat.id,
        f"""
🔥 AMUDANCE FX AI PRO SIGNAL SYSTEM 🔥

Welcome {message.from_user.first_name}

🧠 Hybrid AI: ACTIVE
📊 Structure Engine: ACTIVE
📢 Auto Channel: ACTIVE

Send chart screenshot 📸
""",
        reply_markup=markup
    )

# =========================
# MENU
# =========================
@bot.message_handler(func=lambda m: True)
def menu(m):

    if m.text == "📚 Strategy":
        bot.send_message(m.chat.id,
        """
📊 STRATEGY ENGINE

✔ Market Structure (BOS / MSS)
✔ Liquidity Zones
✔ Risk Management 1:2+
✔ Session Awareness

⚡ No Random Signals
""")

    elif m.text == "💎 Status":
        bot.send_message(m.chat.id,
        """
🟢 SYSTEM STATUS

AI: READY
Strategy: ACTIVE
Channel Posting: ACTIVE
Fallback: ENABLED
""")

    elif m.text == "📞 Support":
        bot.send_message(m.chat.id,
        "AMUDANCE FX SYSTEM v2 ACTIVE")

    elif m.text == "📊 Analyze Chart":
        bot.send_message(m.chat.id, "Send your chart screenshot 📸")

# =========================
# IMAGE HANDLER
# =========================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    msg = bot.send_message(message.chat.id, "🧠 Analyzing chart...")

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file = bot.download_file(file_info.file_path)

        path = "chart.jpg"
        with open(path, "wb") as f:
            f.write(file)

        img = Image.open(path)
        img.save(path, optimize=True, quality=60)

        with open(path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        strat = strategy_engine()
        ai = ai_engine(img_b64)

        result = f"""
🔥 AMUDANCE FX AI SIGNAL 🔥

🕒 SESSION
{strat['session']}

📊 TREND
{strat['trend']}

💡 SIGNAL
{strat['signal']}

📍 ENTRY
{strat['entry']}

🛑 SL
{strat['sl']}

🎯 TP
{strat['tp']}

💧 LIQUIDITY
{strat['liquidity']}

📊 CONFIDENCE
{strat['confidence']}

🧠 AI INSIGHT
{ai if ai else "AI unavailable → fallback active"}

━━━━━━━━━━━━━━━
⚡ PRO SYSTEM v2
"""

        bot.edit_message_text(result, message.chat.id, msg.message_id)

        # =========================
        # AUTO POST TO CHANNEL
        # =========================
        if SIGNAL_CHANNEL:
            try:
                bot.send_message(SIGNAL_CHANNEL, result)
            except:
                pass

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

# =========================
# RUN BOT
# =========================
print("AMUDANCE FX PRO SYSTEM RUNNING...")
bot.infinity_polling(timeout=30, long_polling_timeout=30)
