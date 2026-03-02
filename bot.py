import telebot
import os
import time
from iq_connector import ConectorIQ
from strategy import analizar

# ==========================
# VARIABLES DE ENTORNO
# ==========================

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

# ==========================
# INICIALIZAR BOT
# ==========================

bot = telebot.TeleBot(TOKEN)

# ==========================
# CONECTAR A IQ OPTION
# ==========================

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

if conector.conectar():
    print("✅ Conectado a IQ Option")
else:
    print("❌ Error de conexión IQ Option")

# ==========================
# COMANDO /comenzar
# ==========================

@bot.message_handler(commands=['comenzar'])
def comenzar(mensaje):
    bot.reply_to(mensaje, "🤖 Bot OTC Profesional Activo")

# ==========================
# MENSAJES NORMALES
# ==========================

@bot.message_handler(func=lambda mensaje: True)
def manejar_mensaje(mensaje):
    texto = mensaje.text.lower()

    if "eur usd" in texto:

        # Mensaje inmediato
        bot.reply_to(
            mensaje,
            "🔎 Analizando el gráfico para buscar la mejor entrada..."
        )

        try:
            velas = conector.obtener_velas("EURUSD-OTC", 60, 120)
            señal = analizar(velas)

            bot.send_message(
                mensaje.chat.id,
                señal
            )

        except Exception as e:
            print("Error:", e)
            bot.send_message(
                mensaje.chat.id,
                "⚠ Error analizando el mercado. Intentando nuevamente..."
            )

    else:
        bot.reply_to(mensaje, "Escribe: EUR USD")

# ==========================
# INICIAR BOT
# ==========================
bot.remove_webhook()
time.sleep(2)
while True:
    try:
        print("🚀 Bot corriendo...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Error en polling:", e)
        time.sleep(5)
