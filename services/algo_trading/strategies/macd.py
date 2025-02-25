import pandas as pd
import requests
from datetime import datetime, timedelta, UTC
import time


def get_historical_prices(symbol="BTCUSDT", interval="1h", days=7, retries=3, delay=5):
    """
    Получает исторические цены с Binance за последние `days` дней.
    Повторяет запрос `retries` раз в случае ошибки.
    """
    end_time = int(datetime.now(UTC).timestamp() * 1000)
    start_time = int((datetime.now(UTC) - timedelta(days=days)).timestamp() * 1000)
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
        "limit": 1000,
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Вызывает ошибку, если статус != 200
            data = response.json()
            return pd.Series([float(candle[4]) for candle in data])  # Цена закрытия
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса ({attempt + 1}/{retries}): {e}")
            time.sleep(delay)  # Подождать перед повторной попыткой

    raise ConnectionError("Не удалось получить данные с Binance после нескольких попыток.")


def macd_strategy(prices, short_period=12, long_period=26, signal_period=9):
    """
    Реализация стратегии MACD.
    """
    df = pd.DataFrame(prices, columns=["price"])
    df["EMA_short"] = df["price"].ewm(span=short_period, adjust=False).mean()
    df["EMA_long"] = df["price"].ewm(span=long_period, adjust=False).mean()
    df["MACD"] = df["EMA_short"] - df["EMA_long"]
    df["Signal"] = df["MACD"].ewm(span=signal_period, adjust=False).mean()

    if df["MACD"].iloc[-1] > df["Signal"].iloc[-1]:
        return "BUY"
    elif df["MACD"].iloc[-1] < df["Signal"].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"


def analyze_macd(symbol="BTCUSDT", interval="1h"):
    """
    Анализирует MACD на основе данных за последнюю неделю.
    """
    prices = get_historical_prices(symbol, interval)
    return macd_strategy(prices)


