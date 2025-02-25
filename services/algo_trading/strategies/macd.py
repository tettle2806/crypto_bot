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


def macd_strategy(prices, short_period=12, long_period=26, signal_period=9):
    """
    Реализация стратегии MACD.
    """
    df = pd.DataFrame(prices, columns=["price"])
    df["EMA_short"] = df["price"].ewm(span=short_period, adjust=False).mean()
    df["EMA_long"] = df["price"].ewm(span=long_period, adjust=False).mean()
    df["MACD"] = df["EMA_short"] - df["EMA_long"]
    df["Signal"] = df["MACD"].ewm(span=signal_period, adjust=False).mean()

    return df


def rsi_strategy(prices, period=14, overbought=70, oversold=30):
    """
    Вычисляет RSI и возвращает последние значения.
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def analyze_macd_rsi(symbol="BTCUSDT", interval="1h"):
    """
    Анализирует MACD и RSI на основе данных за последнюю неделю.
    """
    prices = get_historical_prices(symbol, interval)
    df_macd = macd_strategy(prices)
    rsi = rsi_strategy(prices)

    macd_last = df_macd["MACD"].iloc[-1]
    signal_last = df_macd["Signal"].iloc[-1]
    rsi_last = rsi.iloc[-1]

    if macd_last > signal_last and rsi_last < 70:
        return "BUY"
    elif macd_last < signal_last and rsi_last > 30:
        return "SELL"
    else:
        return "HOLD"