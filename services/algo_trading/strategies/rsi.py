from services.algo_trading.get_prices import get_historical_prices


def rsi_strategy(
    symbol="BTCUSDT", interval="1h", period=14, overbought=70, oversold=30
):
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
