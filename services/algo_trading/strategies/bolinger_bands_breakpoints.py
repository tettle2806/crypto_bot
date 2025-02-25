import ccxt
import pandas as pd
import pandas_ta as ta

def fetch_binance_data(symbol="BTC/USDT", timeframe="1m", limit=1000):
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



def calculate_bollinger_bands(data, period=50, std_dev=2):
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
    Генерирует торговые сигналы на основе Bollinger Bands с фильтром тренда EMA(50).
    """
    data = data.copy()
    data['EMA_50'] = ta.ema(data['close'], length=50)  # Фильтр тренда
    adx = ta.adx(data['high'], data['low'], data['close'], length=14)
    data['ADX'] = adx['ADX_14']  # Берём только сам ADX

    data.loc[data['ADX'] < 20, 'Signal'] = "HOLD"


    # Покупка: если цена пробила верхнюю границу и выше EMA
    data.loc[(data['close'] > data['Upper']) & (data['close'].shift(1) <= data['Upper']) & (data['close'] > data['EMA_50']), 'Signal'] = "BUY"

    # Продажа: если цена пробила нижнюю границу и ниже EMA
    data.loc[(data['close'] < data['Lower']) & (data['close'].shift(1) >= data['Lower']) & (data['close'] < data['EMA_50']), 'Signal'] = "SELL"


    return data


# Тестируем
data = generate_signals(calculate_bollinger_bands(fetch_binance_data(limit=2000)))

