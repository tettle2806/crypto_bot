import pandas as pd
import requests
from datetime import datetime, timedelta, UTC


def get_historical_prices(symbol="BTCUSDT", interval="1h", days=7):
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
    return pd.Series(prices)


def rsi_strategy(symbol="BTCUSDT", interval="1h", period=14, overbought=70, oversold=30):
    """
    Стратегия RSI: анализирует последние данные и возвращает торговый сигнал.
    """
    prices = get_historical_prices(symbol, interval)

    # Вычисление разницы цен
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Определение торгового сигнала
    if rsi.iloc[-1] > overbought:
        return "SELL"
    elif rsi.iloc[-1] < oversold:
        return "BUY"
    else:
        return "HOLD"


# Пример использования

