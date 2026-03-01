import telebot
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Bot activo 📊")

@bot.message_handler(content_types=['text'])
def signal(message):
    bot.reply_to(message, "Señal CALL 🟢\nExpira en 5 minutos")

bot.infinity_polling()
