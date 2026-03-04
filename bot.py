import telebot
import os
import time
import random
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

# Diccionario correcto de pares
PARES_OTC = {
    "EURUSDOTC": "EURUSD-OTC",
    "GBPUSDOTC": "GBPUSD-OTC",
    "CADCHFOTC": "CADCHF-OTC",
    "AUDCADOTC": "AUDCAD-OTC"
}

# =====================================
# COMANDO /comenzar
# =====================================

@bot.message_handler(commands=['comenzar'])
def comenzar(mensaje):
    bot.reply_to(
        mensaje,
        "🤖 Bot OTC Profesional Activo\n\n"
        "Comandos:\n"
        "/auto → Señales automáticas\n"
        "/stop → Detener automáticas\n\n"
        "Análisis manual:\n"
        "EURUSDOTC\n"
        "GBPUSDOTC\n"
        "CADCHFOTC\n"
        "AUDCADOTC\n"
    )

# =====================================
# ACTIVAR AUTOMÁTICO
# =====================================

@bot.message_handler(commands=['auto'])
def activar_auto(mensaje):
    global AUTO, CHAT_ID
    AUTO = True
    CHAT_ID = mensaje.chat.id
    bot.reply_to(mensaje, "🚀 Señales automáticas activadas")

@bot.message_handler(commands=['stop'])
def detener_auto(mensaje):
    global AUTO
    AUTO = False
    bot.reply_to(mensaje, "⛔ Señales automáticas detenidas")

# =====================================
# MENSAJES MANUALES
# =====================================

@bot.message_handler(func=lambda mensaje: True)
def manejar_mensaje(mensaje):

    texto = mensaje.text.upper().replace(" ", "")

    if texto in PARES_OTC:

        par = PARES_OTC[texto]

        bot.reply_to(
            mensaje,
            f"🔎 Analizando {par}...\nBuscando la mejor entrada..."
        )

        try:
            velas = conector.obtener_velas(par, 60, 120)

            if not velas:
                bot.send_message(
                    mensaje.chat.id,
                    "⚠ No se pudieron obtener datos"
                )
                return

            señal = analizar(velas)

            bot.send_message(
                mensaje.chat.id,
                f"📊 Par: {par}\n\n{señal}"
            )

        except Exception as e:
            print("Error analizando:", e)
            bot.send_message(
                mensaje.chat.id,
                "⚠ Error analizando mercado"
            )

    else:
        bot.reply_to(
            mensaje,
            "📌 Pares OTC disponibles:\n\n"
            "EURUSDOTC\n"
            "GBPUSDOTC\n"
            "CADCHFOTC\n"
            "AUDCADOTC\n"
        )

# =====================================
# ESPERAR CIERRE EXACTO DE VELA M1
# =====================================

def esperar_cierre_vela():
    while True:
        segundos = int(time.time()) % 60
        if segundos == 0:
            break
        time.sleep(0.5)

# =====================================
# LOOP AUTOMÁTICO
# =====================================

def loop_automatico():
    global AUTO, CHAT_ID, ULTIMA_SEÑAL

    while True:

        if AUTO and CHAT_ID:

            print("⏳ Esperando cierre de vela...")
            esperar_cierre_vela()

            for clave, par in PARES_OTC.items():

                try:
                    velas = conector.obtener_velas(par, 60, 120)

                    if not velas:
                        continue

                    resultado = analizar(velas)

                    if "CALL" in resultado or "PUT" in resultado:

                        if ULTIMA_SEÑAL.get(par) != resultado:

                            bot.send_message(
                                CHAT_ID,
                                f"📊 {par}\n\n"
                                f"{resultado}\n\n"
                                f"🕐 Entrada al inicio de esta nueva vela"
                            )

                            ULTIMA_SEÑAL[par] = resultado

                            velas_espera = random.randint(3, 5)
                            print(f"Esperando {velas_espera} velas...")
                            time.sleep(velas_espera * 60)

                    else:
                        print(f"{par} sin señal clara")

                except Exception as e:
                    print("Error automático:", e)
                    conectar_iq()

        time.sleep(1)

threading.Thread(target=loop_automatico, daemon=True).start()

# =====================================
# INICIAR BOT
# =====================================

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
