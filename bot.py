import telebot
import os
import time
import threading
from iq_connector import ConectorIQ
from strategy import analizar

# ==============================
# VARIABLES
# ==============================

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

if not TOKEN:
    raise Exception("TOKEN no configurado")

bot = telebot.TeleBot(TOKEN)

# Limpiar webhook
try:
    bot.remove_webhook()
except:
    pass

time.sleep(2)

# ==============================
# CONEXIÓN IQ
# ==============================

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

def conectar_iq():
    try:
        if conector.conectar():
            print("✅ Conectado a IQ Option")
        else:
            print("❌ Error conectando IQ")
    except Exception as e:
        print("Error IQ:", e)

conectar_iq()

# ==============================
# CONTROL AUTO
# ==============================

CHAT_ID = None
AUTO_ACTIVO = False

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🤖 Bot activo.\nUsa /auto para señales automáticas")

@bot.message_handler(commands=['auto'])
def auto_on(m):
    global CHAT_ID, AUTO_ACTIVO
    CHAT_ID = m.chat.id
    AUTO_ACTIVO = True
    bot.reply_to(m, "🚀 Señales automáticas activadas")

@bot.message_handler(commands=['stop'])
def auto_off(m):
    global AUTO_ACTIVO
    AUTO_ACTIVO = False
    bot.reply_to(m, "⛔ Señales detenidas")

# ==============================
# SEÑALES AUTOMÁTICAS
# ==============================

def loop_senales():
    global AUTO_ACTIVO

    while True:
        if AUTO_ACTIVO and CHAT_ID:

            for par in ["EURUSD-OTC", "GBPUSD-OTC"]:
                try:
                    velas = conector.obtener_velas(par, 60, 120)

                    if velas:
                        señal = analizar(velas)
                        bot.send_message(CHAT_ID, f"📊 {par}\n\n{señal}")

                except Exception as e:
                    print("Error señal:", e)
                    conectar_iq()

        time.sleep(300)

threading.Thread(target=loop_senales, daemon=True).start()

# ==============================
# POLLING SEGURO SIN 409
# ==============================

def polling_seguro():
    while True:
        try:
            print("🚀 Bot corriendo...")
            bot.polling(none_stop=True, interval=2, timeout=60)
        except Exception as e:
            print("⚠ Error polling:", e)
            time.sleep(10)

if __name__ == "__main__":
    polling_seguro() 
