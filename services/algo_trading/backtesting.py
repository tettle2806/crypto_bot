from services.algo_trading.strategies.bolinger_bands_breakpoints import data


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



# Тестируем бэктест
final_balance = backtest_strategy(data)
print(f"\n💰 Итоговый баланс: {final_balance:.2f} USDT")
