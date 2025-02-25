import pandas as pd
import requests
from datetime import datetime, timedelta, UTC

# Таймфреймы для комбинированного анализа
TIMEFRAMES = {
    "short": {"interval": "5m", "short_window": 5, "long_window": 30},
    "medium": {"interval": "1h", "short_window": 10, "long_window": 50},
    "long": {"interval": "1d", "short_window": 50, "long_window": 200},
}

def get_historical_prices(symbol="BTCUSDT", interval="1h", days=150):
    """
    Получает исторические цены с Binance за последние `days` дней.
    """
    end_time = int(datetime.now(UTC).timestamp() * 1000)
    start_time = int((datetime.now(UTC) - timedelta(days=days)).timestamp() * 1000)

    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
        "limit": 1000,
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Извлекаем цены закрытия
    prices = [float(candle[4]) for candle in data]  # Индекс 4 — цена закрытия
    return prices

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


