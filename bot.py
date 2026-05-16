import os
from flask import Flask, request
import telebot

# ======================
# ENV (Railway or local .env)
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # example: -100xxxxxxxxxx

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ======================
# HOME ROUTE (Railway check)
# ======================
@app.route('/')
def home():
    return "AMUDANCE FX SIGNAL BOT RUNNING ✅"

# ======================
# TRADINGVIEW WEBHOOK
# ======================
@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

    if not data:
        return "No data", 400

    try:
        pair = data.get("pair", "UNKNOWN")
        signal = data.get("signal", "NO SIGNAL")
        entry = data.get("entry", "N/A")
        sl = data.get("sl", "N/A")
        tp = data.get("tp", "N/A")
        timeframe = data.get("timeframe", "M15")
        confidence = data.get("confidence", "60%")

        message = f"""
🔥 AMUDANCE FX SIGNAL 🔥

📊 PAIR: {pair}
⏱ TIMEFRAME: {timeframe}

💡 SIGNAL: {signal}

📍 ENTRY: {entry}
🛑 SL: {sl}
🎯 TP: {tp}

📊 CONFIDENCE: {confidence}

━━━━━━━━━━━━━━━
⚡ Powered by TradingView Engine
🛡 No AI Delay System
"""

        bot.send_message(CHANNEL_ID, message)

        return "OK", 200

    except Exception as e:
        return str(e), 500

# ======================
# START SERVER
# ======================
if __name__ == "__main__":
    print("AMUDANCE FX SIGNAL BOT RUNNING...")
    app.run(host="0.0.0.0", port=8080)
