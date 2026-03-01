import telebot
import os
import requests
import pandas as pd
import ta

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_signal():
    url = "https://api.binance.com/api/v3/klines?symbol=EURUSDT&interval=1m&limit=50"
    data = requests.get(url).json()

    closes = [float(candle[4]) for candle in data]
    df = pd.DataFrame(closes, columns=["close"])

    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    df["ema"] = df["close"].ewm(span=14).mean()

    last_rsi = df["rsi"].iloc[-1]
    last_price = df["close"].iloc[-1]
    last_ema = df["ema"].iloc[-1]

    if last_rsi < 30 and last_price > last_ema:
        return "📈 COMPRA (CALL)\n⏱ Expira en 5 minutos"
    elif last_rsi > 70 and last_price < last_ema:
        return "📉 VENTA (PUT)\n⏱ Expira en 5 minutos"
    else:
        return "⚠️ Sin señal clara ahora"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot activo 📊")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()

    if "eur" in text:
        signal = get_signal()
        bot.reply_to(message, signal)
    else:
        bot.reply_to(message, "Escribe: eur usd")

bot.infinity_polling()
