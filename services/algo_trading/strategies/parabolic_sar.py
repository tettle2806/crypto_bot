import pandas as pd
import requests
from datetime import datetime, timedelta, UTC
import time
import ta


def get_historical_high_low_prices(
    symbol="BTCUSDT", interval="1h", days=7, retries=3, delay=5
):
    """
    Получает исторические максимальные и минимальные цены свечей.
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
            high_prices = [float(candle[2]) for candle in data]
            low_prices = [float(candle[3]) for candle in data]
            return pd.Series(high_prices), pd.Series(low_prices)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса ({attempt + 1}/{retries}): {e}")
            time.sleep(delay)

    raise ConnectionError(
        "Не удалось получить данные с Binance после нескольких попыток."
    )


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

    raise ConnectionError(
        "Не удалось получить данные с Binance после нескольких попыток."
    )


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


def sma_strategy(prices, short_window=10, long_window=50):
    """
    Реализация стратегии SMA.
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


def bollinger_bands_strategy(prices, window=20, num_std=2):
    """
    Реализация стратегии полос Боллинджера.
    """
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


def parabolic_sar_strategy(
    symbol="BTCUSDT", interval="1h", days=7, step=0.02, max_step=0.2
):
    """
    Реализация стратегии Parabolic SAR с дополнительными фильтрами ADX, EMA, MACD и RSI.
    """
    prices = get_historical_prices(symbol, interval, days)
    high, low = get_historical_high_low_prices(symbol, interval, days)

    df = pd.DataFrame({"high": high, "low": low, "close": prices})
    df["SAR"] = ta.trend.PSARIndicator(
        df["high"], df["low"], step=step, max_step=max_step, close=df["close"]
    ).psar()
    df["ADX"] = ta.trend.ADXIndicator(df["high"], df["low"], df["close"]).adx()
    df["EMA_short"] = df["close"].ewm(span=12, adjust=False).mean()
    df["EMA_long"] = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA_short"] - df["EMA_long"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    buy_signal = (
        df["SAR"].iloc[-1] < df["close"].iloc[-1]
        and df["ADX"].iloc[-1] > 25
        and df["EMA_short"].iloc[-1] > df["EMA_long"].iloc[-1]
        and df["MACD"].iloc[-1] > df["Signal"].iloc[-1]
        and 40 <= df["RSI"].iloc[-1] <= 70
    )

    sell_signal = (
        df["SAR"].iloc[-1] > df["close"].iloc[-1]
        and df["ADX"].iloc[-1] > 25
        and df["EMA_short"].iloc[-1] < df["EMA_long"].iloc[-1]
        and df["MACD"].iloc[-1] < df["Signal"].iloc[-1]
        and df["RSI"].iloc[-1] < 30
    )

    if buy_signal:
        return "BUY"
    elif sell_signal:
        return "SELL"
    else:
        return "HOLD"


print(parabolic_sar_strategy())
