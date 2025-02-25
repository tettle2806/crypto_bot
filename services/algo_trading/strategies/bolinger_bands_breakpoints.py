import ccxt
import pandas as pd
import pandas_ta as ta

def fetch_binance_data(symbol="BTC/USDT", timeframe="1h", limit=100):
    """
    Получает исторические данные с Binance.

    :param symbol: Торговая пара (например, "BTC/USDT")
    :param timeframe: Таймфрейм свечей (например, "1h", "15m")
    :param limit: Количество свечей
    :return: DataFrame с историческими данными
    """
    exchange = ccxt.binance()
    candles = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # Преобразуем время

    return df



def calculate_bollinger_bands(data, period=20, std_dev=2):
    """
    Рассчитывает полосы Боллинджера.

    :param data: DataFrame с колонкой 'close'
    :param period: Период для расчета SMA
    :param std_dev: Количество стандартных отклонений
    :return: DataFrame с добавленными колонками ['SMA', 'Upper', 'Lower']
    """
    bb = ta.bbands(data['close'], length=period, std=std_dev)

    if bb is not None:
        data['SMA'] = bb[f'BBM_{period}_{std_dev}.0']
        data['Upper'] = bb[f'BBU_{period}_{std_dev}.0']
        data['Lower'] = bb[f'BBL_{period}_{std_dev}.0']

    else:
        raise ValueError("Ошибка при расчете Bollinger Bands")

    return data


def generate_signals(data):
    """
    Генерирует торговые сигналы на основе пробоя Bollinger Bands.

    :param data: DataFrame с колонками ['close', 'Upper', 'Lower']
    :return: DataFrame с колонкой 'Signal' (buy/sell/hold)
    """
    data = data.copy()
    data['Signal'] = "HOLD"  # По умолчанию держим позицию

    # Покупка, если цена пробивает верхнюю границу
    data.loc[data['close'] > data['Upper'], 'Signal'] = "BUY"

    # Продажа, если цена пробивает нижнюю границу
    data.loc[data['close'] < data['Lower'], 'Signal'] = "SELL"

    return data


# Тестируем
data = generate_signals(calculate_bollinger_bands(fetch_binance_data(limit=1000)))
print(data[['timestamp', 'close', 'Upper', 'Lower', 'Signal']].tail(10))
