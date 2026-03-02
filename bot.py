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

if not TOKEN:
    raise ValueError("TOKEN no configurado")

if not IQ_EMAIL or not IQ_PASSWORD:
    raise ValueError("Credenciales IQ no configuradas")

# ==========================
# INICIALIZAR BOT
# ==========================

bot = telebot.TeleBot(TOKEN)

# Eliminar webhook viejo (evita error 409)
bot.remove_webhook()
time.sleep(2)

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
    texto = mensaje.text.upper().replace(" ", "")

    # Diccionario de pares disponibles
    pares = {
        "EURUSD": "EURUSD",
        "GBPUSD": "GBPUSD",
        "USDJPY": "USDJPY",
        "EURJPY": "EURJPY",
        "AUDUSD": "AUDUSD",
        "EURUSDOTC": "EURUSD-OTC",
        "GBPUSDOTC": "GBPUSD-OTC"
    }

    if texto in pares:

        par = pares[texto]

        bot.reply_to(
            mensaje,
            f"🔎 Analizando {par}...\nBuscando la mejor entrada..."
        )

        try:
            velas = conector.obtener_velas(par, 60, 120)

            if not velas:
                bot.send_message(
                    mensaje.chat.id,
                    "⚠ No se pudieron obtener datos del mercado"
                )
                return

            señal = analizar(velas)

            bot.send_message(
                mensaje.chat.id,
                f"📊 Par: {par}\n\n{señal}"
            )

        except Exception as e:
            print("Error:", e)
            bot.send_message(
                mensaje.chat.id,
                "⚠ Error analizando el mercado"
            )

    else:
        bot.reply_to(
            mensaje,
            "📌 Pares disponibles:\n"
            "EURUSD\n"
            "GBPUSD\n"
            "USDJPY\n"
            "EURJPY\n"
            "AUDUSD\n"
            "EURUSDOTC\n"
            "GBPUSDOTC"
        )
    texto = mensaje.text.lower()

    if "eur usd" in texto:

        bot.reply_to(
            mensaje,
            "🔎 Analizando el gráfico para buscar la mejor entrada..."
        )

        try:
            velas = conector.obtener_velas("EURUSD-OTC", 60, 120)

            if not velas:
                bot.send_message(
                    mensaje.chat.id,
                    "⚠ No se pudieron obtener datos del mercado"
                )
                return

            señal = analizar(velas)

            bot.send_message(
                mensaje.chat.id,
                señal
            )

        except Exception as e:
            print("Error analizando:", e)
            bot.send_message(
                mensaje.chat.id,
                "⚠ Error analizando el mercado. Intenta nuevamente."
            )

    else:
        bot.reply_to(mensaje, "Escribe: EUR USD")

# ==========================
# INICIAR BOT ESTABLE
# ==========================

def iniciar_bot():
    while True:
        try:
            print("🚀 Bot corriendo...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("Error en polling:", e)
            time.sleep(5)

if __name__ == "__main__":
    iniciar_bot()
