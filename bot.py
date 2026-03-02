@bot.message_handler(func=lambda mensaje: True)
def manejar_mensaje(mensaje):
    texto = mensaje.text.upper().replace(" ", "")

    pares_otc = {
        "EURUSDOTC": "EURUSD-OTC",
        "GBPUSDOTC": "GBPUSD-OTC"
    }

    if texto in pares_otc:

        par = pares_otc[texto]

        bot.reply_to(
            mensaje,
            f"🔎 Analizando {par} en OTC...\nBuscando la mejor entrada..."
        )

        try:
            velas = conector.obtener_velas(par, 60, 120)

            if not velas:
                bot.send_message(
                    mensaje.chat.id,
                    "⚠ No se pudieron obtener datos del mercado OTC"
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
                "⚠ Error analizando el mercado OTC"
            )

    else:
        bot.reply_to(
            mensaje,
            "📌 Escribe uno de estos pares OTC:\n"
            "EURUSDOTC\n"
            "GBPUSDOTC"
        )
