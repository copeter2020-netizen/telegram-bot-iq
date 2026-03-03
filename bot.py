import telebot
import os
import time
import threading
from iq_connector import ConectorIQ
from strategy import analizar

# =====================================
# VARIABLES DE ENTORNO
# =====================================

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

if not TOKEN:
    raise ValueError("TOKEN no configurado en Railway")

bot = telebot.TeleBot(TOKEN)

# Evita conflicto 409
bot.remove_webhook()
time.sleep(2)

# =====================================
# CONEXIÓN IQ OPTION
# =====================================

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

def conectar_iq():
    try:
        if conector.conectar():
            print("✅ Conectado a IQ Option")
        else:
            print("❌ Error conectando a IQ")
    except Exception as e:
        print("Error conexión IQ:", e)

conectar_iq()

# =====================================
# VARIABLES GLOBALES
# =====================================

CHAT_ID_ACTIVO = None

# =====================================
# COMANDOS TELEGRAM
# =====================================

@bot.message_handler(commands=['start'])
def start(mensaje):
    bot.reply_to(mensaje, "🤖 Bot activo.\nUsa /auto para activar señales automáticas")

@bot.message_handler(commands=['auto'])
def activar_auto(mensaje):
    global CHAT_ID_ACTIVO
    CHAT_ID_ACTIVO = mensaje.chat.id
    bot.reply_to(mensaje, "🚀 Señales automáticas activadas cada 5 minutos")

@bot.message_handler(commands=['stop'])
def detener_auto(mensaje):
    global CHAT_ID_ACTIVO
    CHAT_ID_ACTIVO = None
    bot.reply_to(mensaje, "⛔ Señales automáticas detenidas")

@bot.message_handler(func=lambda mensaje: True)
def responder(mensaje):
    bot.reply_to(
        mensaje,
        "Comandos disponibles:\n"
        "/auto → activar señales automáticas\n"
        "/stop → detener señales"
    )

# =====================================
# SEÑALES AUTOMÁTICAS
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

                        mensaje = f"📊 {par}\n\n{señal}"

                        bot.send_message(CHAT_ID_ACTIVO, mensaje)

                except Exception as e:
                    print("Error obteniendo señal:", e)
                    conectar_iq()

        # Espera 5 minutos
        time.sleep(300)

# Hilo en segundo plano
threading.Thread(target=señales_automaticas, daemon=True).start()

# =====================================
# INICIAR BOT CON PROTECCIÓN 409
# =====================================

def iniciar_bot():
    while True:
        try:
            print("🚀 Bot corriendo...")

            bot.remove_webhook()
            time.sleep(2)

            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                skip_pending=True
            )

        except Exception as e:
            print("⚠ Error polling:", e)
            print("Reintentando en 15 segundos...")
            time.sleep(15)

if __name__ == "__main__":
    iniciar_bot()
