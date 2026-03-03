import os
import time
import telebot
from iq_connector import ConectorIQ
from strategy import analizar

# =============================
# VARIABLES DE ENTORNO
# =============================

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

if not TOKEN:
    raise Exception("TOKEN no configurado")

# =============================
# CREAR BOT
# =============================

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# 🔥 ELIMINAR CUALQUIER WEBHOOK
try:
    bot.delete_webhook()
    print("Webhook eliminado")
except:
    pass

time.sleep(3)

# =============================
# CONECTAR IQ OPTION
# =============================

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

if conector.conectar():
    print("✅ Conectado a IQ Option")
else:
    print("❌ Error conectando a IQ")

# =============================
# PARES A ANALIZAR
# =============================

PARES = ["EURUSD-OTC", "GBPUSD-OTC"]

CHAT_ID = None
AUTO = False

# =============================
# COMANDOS
# =============================

@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(msg, "🤖 Bot activo\nUsa /auto para señales automáticas")

@bot.message_handler(commands=["auto"])
def auto(msg):
    global CHAT_ID, AUTO
    CHAT_ID = msg.chat.id
    AUTO = True
    bot.reply_to(msg, "🚀 Señales automáticas activadas")

@bot.message_handler(commands=["stop"])
def stop(msg):
    global AUTO
    AUTO = False
    bot.reply_to(msg, "⛔ Señales detenidas")

# =============================
# LOOP AUTOMÁTICO
# =============================

def loop():
    global AUTO

    while True:
        if AUTO and CHAT_ID:
            for par in PARES:
                try:
                    velas = conector.obtener_velas(par, 60, 100)

                    if velas:
                        resultado = analizar(velas)
                        bot.send_message(
                            CHAT_ID,
                            f"📊 <b>{par}</b>\n\n{resultado}"
                        )

                except Exception as e:
                    print("Error señal:", e)

        time.sleep(300)

import threading
threading.Thread(target=loop, daemon=True).start()

# =============================
# POLLING ESTABLE
# =============================

if __name__ == "__main__":
    while True:
        try:
            print("🚀 Bot corriendo...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("Error polling:", e)
            time.sleep(15) 
