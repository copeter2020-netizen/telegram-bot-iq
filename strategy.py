
import pandas as pd
import ta

def analyze(candles):
    df = pd.DataFrame(candles)
    df["close"] = df["close"]

    # Indicadores
    df["ema20"] = ta.trend.ema_indicator(df["close"], window=20)
    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)
    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    last = df.iloc[-1]

    # Lógica avanzada
    if (
        last["ema20"] > last["ema50"]
        and last["rsi"] > 55
        and last["macd"] > last["macd_signal"]
    ):
        return "🟢 COMPRA (CALL)\n⏱ Expira en 5 minutos\n📈 Tendencia alcista confirmada"

    elif (
        last["ema20"] < last["ema50"]
        and last["rsi"] < 45
        and last["macd"] < last["macd_signal"]
    ):
        return "🔴 VENTA (PUT)\n⏱ Expira en 5 minutos\n📉 Tendencia bajista confirmada"

    else:
        return "⚠️ Sin señal clara ahora"
