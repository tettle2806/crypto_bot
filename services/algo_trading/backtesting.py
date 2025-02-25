import pandas as pd

from services.algo_trading.get_prices import get_historical_prices
from services.algo_trading.strategies.bolinger_bands_breakpoints import data
from services.algo_trading.strategies.bollinger_bands import bollinger_bands_strategy


def backtest_strategy(data, initial_balance=1000, trading_size=0.1, stop_loss=0.1, take_profit=0.3):
    balance = initial_balance
    position = 0
    entry_price = 0
    entry_index = None  # Индекс, когда зашли в сделку

    for index, row in data.iterrows():
        if row['Signal'] == "BUY" and balance > 0:
            position = (balance * trading_size) / row['close']
            entry_price = row['close']
            balance -= position * entry_price
            entry_index = index
            print(f"📈 Покупка: {row['timestamp']} Цена: {row['close']} ADX: {row['ADX']}")

        elif row['Signal'] == "SELL" and position > 0:
            max_hold_bars = 50  # Максимум 50 свечей (можно подстроить)

            if position > 0 and (index - entry_index) >= max_hold_bars:
                print(f"⏳ Вышли из сделки по времени: {row['timestamp']} Цена: {row['close']}")
                balance += position * row['close']
                position = 0
            change = (row['close'] - entry_price) / entry_price
            if change <= -stop_loss:
                print(f"STOP LOSS TRIGGERED (-{stop_loss * 100}%)")
            elif change >= take_profit:
                print(f"TAKE PROFIT TRIGGERED (+{take_profit * 100}%)")

            balance += position * row['close']
            print(f"📉 Продажа: {row['timestamp']} Цена: {row['close']} ADX: {row['ADX']}")
            position = 0

    if position > 0:
        balance += position * data.iloc[-1]['close']

    print("\n📊 Итоговая статистика:")
    print(f"📈 Количество покупок: {len(data[data['Signal'] == 'BUY'])}")
    print(f"📉 Количество продаж: {len(data[data['Signal'] == 'SELL'])}")
    print(f"⚠️ Сделки по стоп-лоссу: {len(data[data['close'] <= entry_price * (1 - stop_loss)])}")
    print(f"🎯 Сделки по тейк-профиту: {len(data[data['close'] >= entry_price * (1 + take_profit)])}")

    print("\n🔍 Последние сделки:")
    print(data[['timestamp', 'close', 'Signal']].tail(20))
    return balance





def backtest_bollinger(prices, initial_balance=1000, trading_size=0.1):
    df = pd.DataFrame(prices, columns=["price"])

    balance = initial_balance
    position = 0
    entry_price = 0
    buys = 0
    sells = 0

    for i in range(len(df)):
        signal = bollinger_bands_strategy(prices[: i + 1])  # Считаем сигналы до текущего момента

        if signal == "BUY" and balance > 0:
            position = (balance * trading_size) / df["price"].iloc[i]
            entry_price = df["price"].iloc[i]
            balance -= position * entry_price
            buys += 1
            print(f"📈 Покупка: Цена {entry_price}")

        elif signal == "SELL" and position > 0:
            balance += position * df["price"].iloc[i]
            position = 0
            sells += 1
            print(f"📉 Продажа: Цена {df['price'].iloc[i]}")

    if position > 0:
        balance += position * df["price"].iloc[-1]

    print("\n📊 Итоговая статистика:")
    print(f"💰 Итоговый баланс: {balance:.2f} USDT")
    print(f"📈 Количество покупок: {buys}")
    print(f"📉 Количество продаж: {sells}")

    return balance


# Пример данных
print(backtest_bollinger(get_historical_prices()))
