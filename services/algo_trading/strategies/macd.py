import pandas as pd
from services.algo_trading.get_prices import get_historical_prices


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
