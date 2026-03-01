import telebot
import os
from iq_connector import IQConnector
from strategy import analyze

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

bot = telebot.TeleBot(TOKEN)

connector = IQConnector(IQ_EMAIL, IQ_PASSWORD)

if connector.connect():
    print("Conectado a IQ Option")
else:
    print("Error conexión IQ")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Bot OTC Profesional Activo")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()

    if "otc" in text:
        candles = connector.get_candles("EURUSD-OTC", 60, 120)
        signal = analyze(candles)
        bot.reply_to(message, signal)
    else:
        bot.reply_to(message, "Escribe: eur usd otc")

bot.infinity_polling() 
