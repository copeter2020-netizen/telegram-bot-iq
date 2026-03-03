import os
import time
import telebot
from iq_connector import ConectorIQ
from strategy import analizar

# =========================
# VARIABLES
# =========================

TOKEN = os.getenv("TOKEN")
IQ_EMAIL = os.getenv("IQ_EMAIL")
IQ_PASSWORD = os.getenv("IQ_PASSWORD")

if not TOKEN:
    raise Exception("TOKEN no configurado")

bot = telebot.TeleBot(TOKEN)

# 🔥 LIMPIAR WEBHOOK Y UPDATES ANTIGUOS
try:
    bot.delete_webhook()
    bot.get_updates(offset=-1)
    print("Sesión Telegram limpia")
except:
    pass

time.sleep(2)

# =========================
# CONEXIÓN IQ
# =========================

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

if conector.conectar():
    print("✅ Conectado a IQ Option")
else:
    print("❌ Error conectando a IQ")

# =========================
# CONFIGURACIÓN
# =========================

PARES = ["EURUSD-OTC", "GBPUSD-OTC"]
CHAT_ID = None
AUTO = False

# =========================
# COMANDOS
# =========================

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🤖 Bot activo\nUsa /auto para señales")

@bot.message_handler(commands=['auto'])
def auto(msg):
    global CHAT_ID, AUTO
    CHAT_ID = msg.chat.id
    AUTO = True
    bot.reply_to(msg, "🚀 Señales activadas")

@bot.message_handler(commands=['stop'])
def stop(msg):
    global AUTO
    AUTO = False
    bot.reply_to(msg, "⛔ Señales detenidas")

# =========================
# LOOP SIN THREAD
# =========================

def ejecutar_senales():
    global AUTO

    if AUTO and CHAT_ID:
        for par in PARES:
            try:
                velas = conector.obtener_velas(par, 60, 100)

                if velas:
                    resultado = analizar(velas)
                    bot.send_message(
                        CHAT_ID,
                        f"📊 {par}\n\n{resultado}"
                    )

            except Exception as e:
                print("Error señal:", e)

# =========================
# MAIN LOOP CONTROLADO
# =========================

if __name__ == "__main__":

    print("🚀 Bot corriendo estable...")

    ultimo_envio = 0

    while True:
        try:
            bot.polling(
                none_stop=True,
                interval=2,
                timeout=30,
                skip_pending=True
            )

        except Exception as e:
            print("Reintentando polling:", e)
            time.sleep(5)

        # Ejecutar señales cada 5 minutos
        if time.time() - ultimo_envio > 300:
            ejecutar_senales()
            ultimo_envio = time.time() 
