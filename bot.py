import telebot
from telebot import types
from flask import Flask, request
import requests
import os
import threading
import logging

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# ENV VARIABLES
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is missing in Railway environment variables")

if not CHAT_ID:
    raise Exception("CHAT_ID is missing in Railway environment variables")

CHAT_ID = int(CHAT_ID)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# =========================
# START COMMAND
# =========================
@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(
        types.KeyboardButton("📊 TradingView Signal"),
        types.KeyboardButton("📈 MT5 Signal")
    )

    markup.add(
        types.KeyboardButton("💎 Status"),
        types.KeyboardButton("📞 Support")
    )

    bot.send_message(
        message.chat.id,
        """
🔥 AMUDANCE TRADING BOT 🔥

✅ TradingView Alerts
✅ MT5 Signals
✅ Auto Telegram Posting
✅ Railway Hosting

Bot is LIVE ⚡
""",
        reply_markup=markup
    )

# =========================
# MENU HANDLER
# =========================
@bot.message_handler(func=lambda m: True)
def menu(message):

    if message.text == "💎 Status":

        bot.send_message(
            message.chat.id,
            """
🟢 SYSTEM STATUS

TradingView Webhook: ACTIVE
Telegram Signals: ACTIVE
Railway Server: ONLINE

⚡ AMUDANCE ENGINE RUNNING
"""
        )

    elif message.text == "📞 Support":

        bot.send_message(
            message.chat.id,
            """
📞 SUPPORT

Creator: AMUDANCE FX BOT
Version: v1.0
"""
        )

# =========================
# WEBHOOK (TRADINGVIEW)
# =========================
@app.route('/webhook', methods=['POST'])
def webhook():

    try:
        data = request.get_json(force=True)

        pair = data.get("pair", "UNKNOWN")
        signal = data.get("signal", "NONE")
        entry = data.get("entry", "N/A")
        sl = data.get("sl", "N/A")
        tp = data.get("tp", "N/A")
        timeframe = data.get("timeframe", "N/A")
        confidence = data.get("confidence", "N/A")

        message = f"""
🔥 AMUDANCE FX SIGNAL 🔥

📊 PAIR: {pair}
💡 SIGNAL: {signal}
📍 ENTRY: {entry}
🛑 STOP LOSS: {sl}
🎯 TAKE PROFIT: {tp}
🕒 TIMEFRAME: {timeframe}
📊 CONFIDENCE: {confidence}

━━━━━━━━━━━━━━━
⚡ TradingView Auto Bot
"""

        bot.send_message(CHAT_ID, message)

        return {"status": "success"}

    except Exception as e:
        return {"error": str(e)}

# =========================
# RUN BOT + FLASK
# =========================
def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot).start()

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
