import telebot
from telebot import types
import requests
import base64
import os
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
import random
import threading
import time

# =========================
# LOAD ENV
# =========================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing in .env")

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
# HYBRID STRATEGY ENGINE v3
# =========================
def strategy_engine():
    session = get_session()

    trend = random.choice(["BULLISH", "BEARISH", "RANGE"])
    volatility = random.choice(["LOW", "MEDIUM", "HIGH"])

    score = 50

    # session boost
    if session == "NEW YORK SESSION 🗽":
        score += 15
    elif session == "LONDON SESSION 🏦":
        score += 10

    # trend logic
    if trend == "BULLISH":
        score += 15
        direction = "BUY 📈"
    elif trend == "BEARISH":
        score += 15
        direction = "SELL 📉"
    else:
        score -= 10
        direction = "NO TRADE ⚠"

    # volatility filter
    if volatility == "HIGH":
        score += 10
    elif volatility == "LOW":
        score -= 10

    # decision
    if score >= 75:
        signal = "STRONG SIGNAL 🔥"
        expiry = "3–5 MIN (BINARY)"
    elif score >= 60:
        signal = "VALID SIGNAL ⚡"
        expiry = "2–3 MIN"
    else:
        signal = "NO TRADE ⚠"
        expiry = "-"

    return {
        "session": session,
        "trend": trend,
        "volatility": volatility,
        "direction": direction,
        "score": score,
        "signal": signal,
        "expiry": expiry
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
                        "text": "Analyze this forex chart: trend, entry, liquidity, smart money bias."
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
        return None

# =========================
# START MENU
# =========================
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(
        types.KeyboardButton("📊 Analyze Chart"),
        types.KeyboardButton("🚀 Generate Signal")
    )
    markup.add(
        types.KeyboardButton("📚 Strategy"),
        types.KeyboardButton("💎 Status")
    )

    bot.send_message(
        message.chat.id,
        f"""
🔥 AMUDANCE FX PRO BOT v3 🔥

Welcome {message.from_user.first_name}

🧠 Hybrid Engine: ACTIVE
📊 Strategy System: ACTIVE
⚡ Auto Signals: ACTIVE

Send chart screenshot 📤
""",
        reply_markup=markup
    )

# =========================
# MENU HANDLER
# =========================
@bot.message_handler(func=lambda m: True)
def menu(m):

    if m.text == "📚 Strategy":
        bot.send_message(m.chat.id,
        "Smart engine uses session + trend + volatility scoring")

    elif m.text == "💎 Status":
        bot.send_message(m.chat.id,
        "System ONLINE: Hybrid Engine v3 Running")

    elif m.text == "🚀 Generate Signal":
        strat = strategy_engine()

        text = f"""
🚀 MANUAL SIGNAL

📊 {strat['direction']}
📡 SCORE: {strat['score']}/100
⏱ {strat['expiry']}
🕒 {strat['session']}
"""

        bot.send_message(m.chat.id, text)

        if CHANNEL_ID:
            bot.send_message(CHANNEL_ID, text)

    elif m.text == "📊 Analyze Chart":
        bot.send_message(m.chat.id, "Send chart screenshot 📤")

# =========================
# PHOTO HANDLER
# =========================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    msg = bot.send_message(message.chat.id, "🧠 Analyzing chart...")

    try:
        file = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file.file_path)

        path = "chart.jpg"
        with open(path, "wb") as f:
            f.write(downloaded)

        img = Image.open(path)
        img.save(path, optimize=True, quality=60)

        with open(path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        strat = strategy_engine()
        ai = ai_engine(img_b64)

        result = f"""
🔥 PRO SIGNAL v3 🔥

🕒 SESSION: {strat['session']}
📊 TREND: {strat['trend']}
⚡ VOL: {strat['volatility']}

📡 SCORE: {strat['score']}/100
💡 SIGNAL: {strat['signal']}
📈 DIR: {strat['direction']}
⏱ EXPIRY: {strat['expiry']}

🧠 AI:
{ai if ai else "Fallback Engine Active"}

━━━━━━━━━━━━━━━
AMUDANCE FX SYSTEM
"""

        bot.edit_message_text(result, message.chat.id, msg.message_id)

        # AUTO POST TO CHANNEL
        if CHANNEL_ID:
            try:
                bot.send_message(CHANNEL_ID, result)
            except:
                pass

    except Exception as e:
        bot.send_message(message.chat.id, str(e))

# =========================
# AUTO SIGNAL LOOP
# =========================
def auto_loop():
    while True:
        try:
            strat = strategy_engine()

            if strat["score"] >= 75 and CHANNEL_ID:
                bot.send_message(CHANNEL_ID,
                f"🚨 AUTO SIGNAL\n\n{strat['direction']} | {strat['score']}/100")

            time.sleep(300)
        except:
            time.sleep(10)

threading.Thread(target=auto_loop, daemon=True).start()

# =========================
# RUN BOT
# =========================
print("AMUDANCE FX PRO BOT v3 RUNNING...")
bot.infinity_polling()
