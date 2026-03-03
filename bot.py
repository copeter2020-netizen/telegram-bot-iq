import telebot
import os
import time
from iq_connector import ConectorIQ
from strategy import analizar

# =====================================
# VARIABLES DE ENTORNO
# =====================================

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

if not TOKEN:
    raise ValueError("TOKEN no configurado")

if not IQ_EMAIL or not IQ_PASSWORD:
    raise ValueError("Credenciales IQ no configuradas")

# =====================================
# CREAR BOT
# =====================================

bot = telebot.TeleBot(TOKEN)

# 🔥 IMPORTANTE: evita error 409
bot.remove_webhook()
time.sleep(3)

# =====================================
# CONECTAR A IQ OPTION
# =====================================

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

def conectar_iq():
    if conector.conectar():
        print("✅ Conectado a IQ Option")
    else:
        print("❌ Error de conexión IQ Option")

conectar_iq()

# =====================================
# COMANDO /comenzar
# =====================================

@bot.message_handler(commands=['comenzar'])
def comenzar(mensaje):
    bot.reply_to(
        mensaje,
        "🤖 Bot OTC Profesional Activo\n\n"
        "Pares disponibles:\n"
        "EURUSDOTC\n"
        "GBPUSDOTC"
    )

# =====================================
# MENSAJES
# =====================================

@bot.message_handler(func=lambda mensaje: True)
def manejar_mensaje(mensaje):

    texto = mensaje.text.upper().replace(" ", "")

    pares = {
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
            print("Error analizando:", e)

            # 🔁 Intentar reconectar automáticamente
            print("Reintentando conexión a IQ...")
            conectar_iq()

            bot.send_message(
                mensaje.chat.id,
                "⚠ Error temporal. Intentando reconectar..."
            )

    else:
        bot.reply_to(
            mensaje,
            "📌 Escribe uno de estos pares:\n"
            "EURUSDOTC\n"
            "GBPUSDOTC"
        )

# =====================================
# INICIAR BOT ESTABLE
# =====================================

def iniciar_bot():
    while True:
        try:
            print("🚀 Bot corriendo...")
            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                skip_pending=True
            )
        except Exception as e:
            print("Error en polling:", e)
            time.sleep(10)

if __name__ == "__main__":
    iniciar_bot()
