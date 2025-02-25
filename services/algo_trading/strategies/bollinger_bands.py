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
            response.raise_for_status()
            data = response.json()
            return pd.Series([float(candle[4]) for candle in data])  # Цена закрытия
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса ({attempt + 1}/{retries}): {e}")
            time.sleep(delay)

    raise ConnectionError("Не удалось получить данные с Binance после нескольких попыток.")


def bollinger_bands_strategy(prices, window=20, num_std=2):
    df = pd.DataFrame(prices, columns=["price"])
    df["SMA"] = df["price"].rolling(window).mean()
    df["Upper"] = df["SMA"] + (df["price"].rolling(window).std() * num_std)
    df["Lower"] = df["SMA"] - (df["price"].rolling(window).std() * num_std)

    if df["price"].iloc[-1] <= df["Lower"].iloc[-1]:
        return "BUY"
    elif df["price"].iloc[-1] >= df["Upper"].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

