import pandas as pd
from services.algo_trading.get_prices import get_historical_prices

# Таймфреймы для комбинированного анализа
TIMEFRAMES = {
    "short": {"interval": "5m", "short_window": 5, "long_window": 30},
    "medium": {"interval": "1h", "short_window": 10, "long_window": 50},
    "long": {"interval": "1d", "short_window": 50, "long_window": 200},
}


def sma_strategy(prices, short_window=10, long_window=50):
    """
    Стратегия на основе скользящих средних (SMA).
    """
    df = pd.DataFrame(prices, columns=["price"])
    df["SMA_short"] = df["price"].rolling(short_window).mean()
    df["SMA_long"] = df["price"].rolling(long_window).mean()

    if df["SMA_short"].iloc[-1] > df["SMA_long"].iloc[-1]:
        return "BUY"
    elif df["SMA_short"].iloc[-1] < df["SMA_long"].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

def combined_strategy(symbol="BTCUSDT"):
    """
    Анализирует рынок на нескольких таймфреймах и возвращает общий сигнал (BUY, SELL, HOLD).
    """
    signals = {}

    for timeframe, params in TIMEFRAMES.items():
        prices = get_historical_prices(symbol, params["interval"])
        signal = sma_strategy(prices, params["short_window"], params["long_window"])
        signals[timeframe] = signal

    # Логика принятия решения
    if signals["short"] == signals["medium"] == signals["long"] == "BUY":
        return "BUY"
    elif signals["short"] == signals["medium"] == signals["long"] == "SELL":
        return "SELL"
    else:
        return "HOLD"


