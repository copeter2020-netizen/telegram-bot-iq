import telebot
import os
import requests
import pandas as pd
import ta

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_signal():
    url = "https://api.binance.com/api/v3/klines?symbol=EURUSDT&interval=1m&limit=100"
    data = requests.get(url).json()

    closes = [float(candle[4]) for candle in data]
    df = pd.DataFrame(closes, columns=["close"])

    # Indicadores
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()

    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    last = df.iloc[-1]

    # Condiciones profesionales
    if (
        last["ema20"] > last["ema50"]
        and last["rsi"] > 50
        and last["macd"] > last["macd_signal"]
    ):
        return "📈 COMPRA (CALL)\n⏱ Expira en 5 minutos\n📊 Tendencia alcista confirmada"

    elif (
        last["ema20"] < last["ema50"]
        and last["rsi"] < 50
        and last["macd"] < last["macd_signal"]
    ):
        return "📉 VENTA (PUT)\n⏱ Expira en 5 minutos\n📊 Tendencia bajista confirmada"

    else:
        return "⚠️ Sin confirmación suficiente ahora"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot profesional activo 📊🔥")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()

    if "eur" in text:
        signal = get_signal()
        bot.reply_to(message, signal)
    else:
        bot.reply_to(message, "Escribe: eur usd")

bot.infinity_polling()
