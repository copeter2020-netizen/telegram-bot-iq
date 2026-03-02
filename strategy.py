import pandas as pd
import ta

def analizar(velas):

    # ==========================
    # VALIDACIONES
    # ==========================

    if not velas or len(velas) < 60:
        return "⚠ No hay suficientes datos para analizar"

    try:
        df = pd.DataFrame(velas)
    except Exception:
        return "⚠ Error procesando datos"

    if "close" not in df.columns:
        return "⚠ Datos inválidos recibidos"

    # ==========================
    # INDICADORES
    # ==========================

    try:
        df["ema20"] = ta.trend.ema_indicator(df["close"], window=20)
        df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
        df["rsi"] = ta.momentum.rsi(df["close"], window=14)

        macd = ta.trend.MACD(df["close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()

    except Exception:
        return "⚠ Error calculando indicadores"

    df = df.dropna()

    if df.empty:
        return "⚠ Datos insuficientes tras calcular indicadores"

    last = df.iloc[-1]

    # ==========================
    # LÓGICA DE SEÑAL
    # ==========================

    if (
        last["ema20"] > last["ema50"]
        and last["rsi"] > 55
        and last["macd"] > last["macd_signal"]
    ):
        return (
            "🟢 COMPRA (CALL)\n"
            "⏳ Expira en 5 minutos\n"
            "📈 Tendencia alcista confirmada"
        )

    elif (
        last["ema20"] < last["ema50"]
        and last["rsi"] < 45
        and last["macd"] < last["macd_signal"]
    ):
        return (
            "🔴 VENTA (PUT)\n"
            "⏳ Expira en 5 minutos\n"
            "📉 Tendencia bajista confirmada"
        )

    else:
        return (
            "🟡 Sin señal clara ahora\n"
            "⏳ Esperando mejor confirmación"
        )
