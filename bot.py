import telebot
import os
from iq_connector import ConectorIQ
from strategy import analizar

# ==============================
# VARIABLES DE ENTORNO
# ==============================

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

# ==============================
# INICIALIZAR BOT
# ==============================

bot = telebot.TeleBot(TOKEN)

# ==============================
# CONECTAR A IQ OPTION
# ==============================

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

if conector.conectar():
    print("✅ Conectado a IQ Option")
else:
    print("❌ Error de conexión IQ Option")

# ==============================
# COMANDO /comenzar
# ==============================

@bot.message_handler(commands=['comenzar'])
def comenzar(mensaje):
    bot.reply_to(mensaje, "🤖 Bot OTC Profesional Activo")

# ==============================
# MENSAJES NORMALES
# ==============================

@bot.message_handler(func=lambda mensaje: True)
def manejar_mensaje(mensaje):
    texto = mensaje.text.lower()

    if "eur usd" in texto:
        velas = conector.obtener_velas("EUR USD"OTC", 60, 120)
        señal = analizar(velas)
        bot.reply_to(mensaje, señal)
    else:
        bot.reply_to(mensaje, "Escribe: EUR USD")

# ==============================
# INICIAR BOT
# ==============================

if __name__ == "__main__":
    print("🚀 Bot corriendo...")
    bot.infinity_polling()
