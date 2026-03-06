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
    raise ValueError("TOKEN no configurado")

if not IQ_EMAIL or not IQ_PASSWORD:
    raise ValueError("Credenciales IQ no configuradas")

# =====================================
# INICIALIZAR BOT
# =====================================

bot = telebot.TeleBot(TOKEN)

try:
    bot.remove_webhook()
except:
    pass

time.sleep(2)

# =====================================
# CONECTAR A IQ OPTION
# =====================================

conector = ConectorIQ(IQ_EMAIL, IQ_PASSWORD)

def conectar_iq():

    try:
        if conector.conectar():
            print("✅ Conectado a IQ Option")
        else:
            print("❌ Error de conexión IQ Option")

    except Exception as e:
        print("Error conectando IQ:", e)

conectar_iq()

# =====================================
# VARIABLES GLOBALES
# =====================================

AUTO = False
CHAT_ID = None
ULTIMA_SEÑAL = {}

# =====================================
# LISTA DE PARES OTC
# =====================================

PARES_OTC = {
    "EURUSDOTC": "EURUSD-OTC",
    "GBPUSDOTC": "GBPUSD-OTC",
    "AUDCADOTC": "AUDCAD-OTC",
    "AUDUSDOTC": "AUDUSD-OTC",
    "USDJPYOTC": "USDJPY-OTC",
    "EURGBPOTC": "EURGBP-OTC",
    "USDCADOTC": "USDCAD-OTC",
    "EURJPYOTC": "EURJPY-OTC",
    "CADCHFOTC": "CADCHF-OTC"
}

# =====================================
# COMANDO /comenzar
# =====================================

@bot.message_handler(commands=['comenzar'])
def comenzar(mensaje):

    texto = (
        "🤖 BOT OTC ACTIVO\n\n"
        "Comandos:\n"
        "/auto → Activar señales automáticas\n"
        "/stop → Detener señales\n\n"
        "Análisis manual:\n"
        "EURUSDOTC\n"
        "GBPUSDOTC\n"
        "AUDCADOTC\n"
        "AUDUSDOTC\n"
        "USDJPYOTC"
    )

    bot.reply_to(mensaje, texto)

# =====================================
# ACTIVAR AUTOMÁTICO
# =====================================

@bot.message_handler(commands=['auto'])
def activar_auto(mensaje):

    global AUTO, CHAT_ID

    AUTO = True
    CHAT_ID = mensaje.chat.id

    bot.reply_to(mensaje, "🚀 Señales automáticas ACTIVADAS")

# =====================================
# DETENER AUTOMÁTICO
# =====================================

@bot.message_handler(commands=['stop'])
def detener_auto(mensaje):

    global AUTO

    AUTO = False

    bot.reply_to(mensaje, "⛔ Señales automáticas DETENIDAS")

# =====================================
# MENSAJES MANUALES
# =====================================

@bot.message_handler(func=lambda mensaje: True)
def manejar_mensaje(mensaje):

    texto = mensaje.text.upper()

    if texto in PARES_OTC:

        par = PARES_OTC[texto]

        try:

            resultado = analizar(conector, par)

            bot.reply_to(
                mensaje,
                f"📊 ANÁLISIS\n\n"
                f"Par: {par}\n"
                f"{resultado}"
            )

        except Exception as e:

            bot.reply_to(mensaje, f"⚠️ Error analizando {par}")

# =====================================
# SEÑALES AUTOMÁTICAS
# =====================================

def auto_signals():

    global AUTO

    while True:

        if AUTO and CHAT_ID:

            print("🔎 Analizando mercado...")

            for nombre, par in PARES_OTC.items():

                try:

                    señal = analizar(conector, par)

                    if señal and señal != ULTIMA_SEÑAL.get(par):

                        mensaje = (
                            "🚨 SEÑAL DETECTADA\n\n"
                            f"Par: {par}\n"
                            f"{señal}\n\n"
                            "⏱ Expiración: 3-5 minutos"
                        )

                        bot.send_message(CHAT_ID, mensaje)

                        ULTIMA_SEÑAL[par] = señal

                        print("✅ Señal enviada:", par)

                    else:

                        print("⏳ Sin señal:", par)

                except Exception as e:

                    print("⚠️ Error analizando", par, e)

        time.sleep(60)

# =====================================
# INICIAR BOT
# =====================================

threading.Thread(target=auto_signals).start()

print("🚀 Bot corriendo...")

bot.infinity_polling() 
