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
        print("
