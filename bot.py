import telebot
from telebot import types
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
from flask import Flask
import threading
import os
from datetime import datetime

# ==========================================
# LOAD ENV
# ==========================================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY missing")

# ==========================================
# GEMINI CONFIG
# ==========================================
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# ==========================================
# TELEGRAM BOT
# ==========================================
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# FLASK APP (RAILWAY)
# ==========================================
app = Flask(__name__)

@app.route("/")
def home():
    return "AMUDANCE INSTITUTIONAL AI RUNNING"

# ==========================================
# SESSION DETECTION
# ==========================================
def get_session():
    hour = datetime.utcnow().hour

    if 7 <= hour < 12:
        return "LONDON SESSION 🏦"

    elif 12 <= hour < 17:
        return "NEW YORK SESSION 🗽"

    else:
        return "ASIAN SESSION 🌏"

# ==========================================
# START MENU
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("📊 Analyze Chart")
    btn2 = types.KeyboardButton("📚 Strategy")
    btn3 = types.KeyboardButton("💎 Status")
    btn4 = types.KeyboardButton("📞 Support")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)

    welcome = f"""
🔥 AMUDANCE INSTITUTIONAL AI 🔥

Welcome {message.from_user.first_name}

✅ MT5 Analysis
✅ Binary Options Analysis
✅ Smart Money Concepts
✅ Liquidity Detection
✅ Trend Analysis
✅ AI Chart Reading

📤 Send chart screenshot now
"""

    bot.send_message(
        message.chat.id,
        welcome,
        reply_markup=markup
    )

# ==========================================
# MENU SYSTEM
# ==========================================
@bot.message_handler(func=lambda m: True)
def menu_handler(message):

    if message.text == "📚 Strategy":

        text = """
📚 STRATEGY ENGINE

✅ Smart Money Concepts
✅ Liquidity Sweeps
✅ Trend Continuation
✅ BOS Confirmation
✅ RSI + EMA Bias
✅ Binary Options Timing
✅ MT5 Scalping Logic

Best Timeframes:
• M1
• M5
• M15
• H1
"""

        bot.send_message(message.chat.id, text)

    elif message.text == "💎 Status":

        text = """
🟢 SYSTEM STATUS

AI Engine: ONLINE
Gemini Vision: ACTIVE
Railway Server: RUNNING
Signal Engine: READY

⚡ Institutional AI v6
"""

        bot.send_message(message.chat.id, text)

    elif message.text == "📞 Support":

        bot.send_message(
            message.chat.id,
            """
📞 SUPPORT

Creator: Mr. Intellect
Bot: AMUDANCE INSTITUTIONAL AI
Version: v6
"""
        )

    elif message.text == "📊 Analyze Chart":

        bot.send_message(
            message.chat.id,
            """
📤 SEND TRADING SCREENSHOT

Best Results:
✅ Clear candles
✅ TradingView screenshots
✅ MT5 screenshots
✅ Visible timeframe
"""
        )

# ==========================================
# IMAGE ANALYSIS
# ==========================================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    loading = bot.send_message(
        message.chat.id,
        "🧠 Gemini AI analyzing chart..."
    )

    try:

        # DOWNLOAD IMAGE
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        image_path = "chart.jpg"

        with open(image_path, "wb") as f:
            f.write(downloaded)

        image = Image.open(image_path)

        # SESSION
        session = get_session()

        # ==========================================
        # GEMINI PROMPT
        # ==========================================
        prompt = f"""
You are a professional institutional forex and binary options analyst.

Analyze this trading chart professionally.

Give:
1. Trend Direction
2. Buy or Sell
3. Entry Zone
4. Stop Loss
5. Take Profit
6. Market Structure
7. Liquidity Information
8. Confidence Percentage
9. Binary Options Direction
10. Scalping Opportunity

Use clean formatting with emojis.

Session:
{session}

Do NOT say "cannot analyze".

Give direct analysis.
"""

        # ==========================================
        # GEMINI ANALYSIS
        # ==========================================
        response = model.generate_content(
            [prompt, image]
        )

        ai_result = response.text

        # ==========================================
        # FINAL MESSAGE
        # ==========================================
        final = f"""
🔥 AMUDANCE FX AI SIGNAL 🔥

🕒 SESSION
{session}

{ai_result}

━━━━━━━━━━━━━━━

⚡ Gemini Institutional AI
📊 MT5 + Binary Options
🤖 AI Vision Analysis
"""

        # SEND TO USER
        bot.edit_message_text(
            final,
            message.chat.id,
            loading.message_id
        )

        # AUTO POST CHANNEL
        if CHANNEL_ID:

            try:
                bot.send_message(CHANNEL_ID, final)

            except:
                pass

    except Exception as e:

        bot.edit_message_text(
            f"❌ Error:\n{e}",
            message.chat.id,
            loading.message_id
        )

# ==========================================
# HELP COMMAND
# ==========================================
@bot.message_handler(commands=['help'])
def help_command(message):

    help_text = """
📖 COMMANDS

/start - Start bot
/help - Show commands

📤 Send trading screenshot for AI analysis.
"""

    bot.send_message(message.chat.id, help_text)

# ==========================================
# RUN TELEGRAM
# ==========================================
def run_bot():
    print("AMUDANCE INSTITUTIONAL AI RUNNING...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

# ==========================================
# RUN FLASK
# ==========================================
def run_web():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )

# ==========================================
# START BOTH
# ==========================================
threading.Thread(target=run_bot).start()

run_web()
