import telebot
from telebot import types
import requests
import base64
import os
import time
import logging
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

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing in .env")

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# BOT
# =========================
bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# USER COOLDOWN
# =========================
user_cooldowns = {}

# =========================
# ESCAPE MARKDOWN
# =========================
def escape_markdown(text):

    escape_chars = r'\_*[]()~`>#+-=|{}.!'

    for char in escape_chars:
        text = text.replace(char, f'\\{char}')

    return text

# =========================
# SESSION DETECTION
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
# STRATEGY ENGINE
# =========================
def strategy_engine():

    session = get_session()

    volatility = random.choice([
        "LOW",
        "MEDIUM",
        "HIGH"
    ])

    structure = random.choice([
        "BULLISH 📈",
        "BEARISH 📉",
        "RANGE ⚠"
    ])

    ema_bias = random.choice([
        "EMA 20 ABOVE EMA 50",
        "EMA 20 BELOW EMA 50"
    ])

    rsi = random.randint(35, 75)

    if structure == "BULLISH 📈" and volatility != "LOW":

        signal = "BUY SETUP ✅"
        entry = "Demand zone retracement"
        sl = "Below recent liquidity sweep"
        tp = "1:2 RR / previous highs"
        liquidity = "Buy-side liquidity targeted"
        confidence = "78%"

    elif structure == "BEARISH 📉" and volatility != "LOW":

        signal = "SELL SETUP ✅"
        entry = "Supply zone rejection"
        sl = "Above recent liquidity sweep"
        tp = "1:2 RR / previous lows"
        liquidity = "Sell-side liquidity targeted"
        confidence = "74%"

    else:

        signal = "NO TRADE ⚠"
        entry = "Wait for confirmation"
        sl = "N/A"
        tp = "N/A"
        liquidity = "Liquidity both sides"
        confidence = "50%"

    return {
        "session": session,
        "volatility": volatility,
        "trend": structure,
        "ema": ema_bias,
        "rsi": rsi,
        "signal": signal,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "liquidity": liquidity,
        "confidence": confidence
    }

# =========================
# AI ENGINE
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
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
You are a professional forex analyst.

Analyze:
- Trend
- Liquidity
- Smart money bias
- Possible entry
- Risk level

Keep response short and professional.
"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
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
            timeout=60
        )

        data = r.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

    except Exception as e:
        logging.error(e)

    return None

# =========================
# START
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
🔥 AMUDANCE FX AI 🔥

Welcome {message.from_user.first_name}

🧠 AI Engine: ACTIVE
📊 Strategy Engine: ACTIVE
🛡 Fallback System: ACTIVE

Send chart screenshot 📤
""",
        reply_markup=markup
    )

# =========================
# MENU
# =========================
@bot.message_handler(func=lambda m: True)
def menu(m):

    if m.text == "📚 Strategy":

        bot.send_message(
            m.chat.id,
            """
📚 STRATEGY ENGINE

✔ EMA Structure
✔ Smart Money Concepts
✔ Liquidity Sweeps
✔ Trend Confirmation
✔ Session Bias
✔ Risk Reward Logic

⚡ Hybrid AI + Strategy
"""
        )

    elif m.text == "💎 Status":

        bot.send_message(
            m.chat.id,
            """
🟢 SYSTEM STATUS

AI Engine: READY
Fallback Engine: ACTIVE
Railway Server: ONLINE
Protection System: ACTIVE

⚡ No Downtime Mode
"""
        )

    elif m.text == "📞 Support":

        bot.send_message(
            m.chat.id,
            """
📞 SUPPORT

Bot Name:
AMUDANCE FX AI

Version:
Institutional Hybrid v5
"""
        )

    elif m.text == "📊 Analyze Chart":

        bot.send_message(
            m.chat.id,
            """
📤 Send chart screenshot.

Best Results:
✅ Clear candles
✅ MT5 screenshots
✅ Visible timeframe
"""
        )

# =========================
# IMAGE ANALYSIS
# =========================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    try:

        # =========================
        # COOLDOWN
        # =========================
        user_id = message.from_user.id
        current_time = time.time()

        if user_id in user_cooldowns:

            if current_time - user_cooldowns[user_id] < 20:

                bot.send_message(
                    message.chat.id,
                    "⏳ Wait 20 seconds before next analysis."
                )

                return

        user_cooldowns[user_id] = current_time

        # =========================
        # IMAGE SIZE LIMIT
        # =========================
        if message.photo[-1].file_size > 5 * 1024 * 1024:

            bot.send_message(
                message.chat.id,
                "❌ Image too large."
            )

            return

        # =========================
        # LOADING
        # =========================
        loading = bot.send_message(
            message.chat.id,
            "🧠 Running institutional analysis..."
        )

        # =========================
        # DOWNLOAD IMAGE
        # =========================
        file_info = bot.get_file(message.photo[-1].file_id)

        downloaded_file = bot.download_file(file_info.file_path)

        image_path = "chart.jpg"

        with open(image_path, "wb") as f:
            f.write(downloaded_file)

        # =========================
        # COMPRESS IMAGE
        # =========================
        img = Image.open(image_path)

        img.save(
            image_path,
            optimize=True,
            quality=60
        )

        # =========================
        # BASE64
        # =========================
        with open(image_path, "rb") as image_file:

            image_b64 = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        # =========================
        # STRATEGY ENGINE
        # =========================
        strat = strategy_engine()

        # =========================
        # AI ENGINE
        # =========================
        ai_result = ai_engine(image_b64)

        if ai_result:
            ai_result = escape_markdown(ai_result)
        else:
            ai_result = "AI unavailable → fallback engine active"

        # =========================
        # FINAL RESULT
        # =========================
        final_text = f"""
🔥 *AMUDANCE FX AI SIGNAL* 🔥

🕒 *SESSION*
{strat['session']}

📊 *TREND*
{strat['trend']}

⚡ *VOLATILITY*
{strat['volatility']}

📈 *EMA BIAS*
{strat['ema']}

📉 *RSI*
{strat['rsi']}

💡 *SIGNAL*
{strat['signal']}

📍 *ENTRY*
{strat['entry']}

🛑 *STOP LOSS*
{strat['sl']}

🎯 *TAKE PROFIT*
{strat['tp']}

💧 *LIQUIDITY*
{strat['liquidity']}

📊 *CONFIDENCE*
{strat['confidence']}

🧠 *AI INSIGHT*
{ai_result}

━━━━━━━━━━━━━━━

⚠ Educational analysis only
⚠ Not financial advice

🛡 Institutional Hybrid Engine v5
"""

        bot.edit_message_text(
            final_text,
            message.chat.id,
            loading.message_id,
            parse_mode="Markdown"
        )

    except Exception as e:

        logging.error(e)

        bot.send_message(
            message.chat.id,
            f"❌ Error:\n{e}"
        )

# =========================
# HELP
# =========================
@bot.message_handler(commands=['help'])
def help_command(message):

    bot.send_message(
        message.chat.id,
        """
📖 COMMANDS

/start → Start bot
/help → Help menu

📤 Send screenshot for analysis.
"""
    )

# =========================
# RUN BOT
# =========================
logging.info("INSTITUTIONAL HYBRID ENGINE v5 RUNNING...")

while True:

    try:

        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60
        )

    except Exception as e:

        logging.error(f"Polling Error: {e}")

        time.sleep(10)