import telebot
import os
import time
import threading
from iq_connector import ConectorIQ
from strategy import analizar

# =====================================
# VARIABLES
# =====================================

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

if not TOKEN:
    raise ValueError("TOKEN no configurado")

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
time.sleep(2)

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

# Guardará el chat donde enviar señales
CHAT_ID_ACTIVO = None

# =====================================
# CONEXIÓN IQ
# =====================================

def conectar_iq():
    if conector.conectar():
        print("✅ Conectado a IQ Option")
    else:
        print("❌ Error conectando IQ")

conectar_iq()

# =====================================
# COMANDO INICIAR AUTO
# =====================================

@bot.message_handler(commands=['auto'])
def activar_auto(mensaje):
    global CHAT_ID_ACTIVO
    CHAT_ID_ACTIVO = mensaje.chat.id
    bot.reply_to(mensaje, "🚀 Señales automáticas activadas cada 5 minutos")

# =====================================
# COMANDO DETENER
# =====================================

@bot.message_handler(commands=['stop'])
def detener_auto(mensaje):
    global CHAT_ID_ACTIVO
    CHAT_ID_ACTIVO = None
    bot.reply_to(mensaje, "⛔ Señales automáticas detenidas")

# =====================================
# ENVÍO AUTOMÁTICO CADA 5 MINUTOS
# =====================================

def señales_automaticas():
    global CHAT_ID_ACTIVO

    while True:
        if CHAT_ID_ACTIVO:

            pares = ["EURUSD-OTC", "GBPUSD-OTC"]

            for par in pares:
                try:
                    velas = conector.obtener_velas(par, 60, 120)

                    if velas:
                        señal = analizar(velas)

                        bot.send_message(
                            CHAT_ID_ACTIVO,
                            f"📊 {par}\n\n{señal}"
                        )

                except Exception as e:
                    print("Error automático:", e)
                    conectar_iq()

        # Espera 5 minutos
        time.sleep(300)

# =====================================
# RESPUESTA NORMAL
# =====================================

@bot.message_handler(func=lambda mensaje: True)
def responder(mensaje):
    bot.reply_to(
        mensaje,
        "Usa:\n"
        "/auto → activar señales automáticas\n"
        "/stop → detener señales"
    )

# =====================================
# INICIAR THREAD AUTOMÁTICO
# =====================================

threading.Thread(target=señales_automaticas, daemon=True).start()

# =====================================
# INICIAR BOT
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
            print("Error polling:", e)
            time.sleep(10)

if __name__ == "__main__":
    iniciar_bot()
