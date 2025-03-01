# TODO: Стратегия моментум-скэльпинга на криптовалютной бирже Binance
# TODO: РАБОЧАЯ СТРАТЕГИЯ

import requests
import time
import numpy as np
from binance.client import Client

from services.algo_trading.strategies.order_flow_scalping import backtest

# API-ключи Binance (замени на свои)
API_KEY = "G2rAy6PTlNv146by6tsRTQJZvjdporAZYQBwnpJai37qmjQ7XnpHcvAuQiRsrLDP"
API_SECRET = "tlpVGSVnBBV7inGOjpL5BoiqkhBbLVjbQcupWPy7YWg23PL2oJACKmc51KmDgGFp"
client = Client(API_KEY, API_SECRET)
# Пара для торговли
SYMBOL = "BTCUSDT"
QUANTITY = 0.01  # Лот для входа в позицию

# Параметры стратегии
STOP_LOSS = 0.3  # 0.3% от цены входа
TAKE_PROFIT = 0.6  # 0.6% от цены входа
EMA_SHORT = 9  # Короткая EMA
EMA_LONG = 21  # Длинная EMA
RSI_PERIOD = 14  # Период RSI
RSI_OVERBOUGHT = 70  # Перекупленность
RSI_OVERSOLD = 30  # Перепроданность

# Глобальные переменные
data = []
position = None
entry_price = 0


# Функция получения свечей
def fetch_candles():
    global data
    candles = client.get_klines(
        symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1MINUTE, limit=50
    )
    data = [float(candle[4]) for candle in candles]  # Используем цену закрытия
    print(data)


# Функция расчета EMA
def calculate_ema(prices, period):
    return np.convolve(prices, np.ones((period,)) / period, mode="valid")[-1]


# Функция расчета RSI
def calculate_rsi(prices, period=RSI_PERIOD):
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return rsi


# Анализ импульсного движения
def analyze_momentum():
    global position, entry_price
    if len(data) < EMA_LONG:
        return

    ema_short = calculate_ema(data, EMA_SHORT)
    ema_long = calculate_ema(data, EMA_LONG)
    rsi = calculate_rsi(data)

    if ema_short > ema_long and rsi < RSI_OVERSOLD and not position:
        position = "long"
        entry_price = data[-1]
        place_order("BUY")
    elif ema_short < ema_long and rsi > RSI_OVERBOUGHT and not position:
        position = "short"
        entry_price = data[-1]
        place_order("SELL")


# Функция управления позицией
def manage_position(current_price):
    global position, entry_price
    if position:
        stop_loss_price = (
            entry_price * (1 - STOP_LOSS / 100)
            if position == "long"
            else entry_price * (1 + STOP_LOSS / 100)
        )
        take_profit_price = (
            entry_price * (1 + TAKE_PROFIT / 100)
            if position == "long"
            else entry_price * (1 - TAKE_PROFIT / 100)
        )

        if (
            position == "long"
            and (current_price <= stop_loss_price or current_price >= take_profit_price)
        ) or (
            position == "short"
            and (current_price >= stop_loss_price or current_price <= take_profit_price)
        ):
            close_position()


# Функция открытия ордера
def place_order(side):
    print(f"Открытие {side} позиции по {SYMBOL}")
    # client.order_market(symbol=SYMBOL, side=side, quantity=QUANTITY)


# Функция закрытия позиции
def close_position():
    global position
    if position == "long":
        print(f"Закрытие LONG позиции по {SYMBOL}")
        # client.order_market(symbol=SYMBOL, side="SELL", quantity=QUANTITY)
    elif position == "short":
        print(f"Закрытие SHORT позиции по {SYMBOL}")
        # client.order_market(symbol=SYMBOL, side="BUY", quantity=QUANTITY)
    position = None


# Функция для тестирования стратегии на исторических данных за последние две недели
def test_strategy_last_two_weeks():
    candles = client.get_klines(
        symbol=SYMBOL, interval=Client.KLINE_INTERVAL_2HOUR, limit=2000
    )
    historical_data = [float(candle[4]) for candle in candles]  # Цена закрытия
    return backtest(historical_data)


# Основной цикл
while True:
    fetch_candles()
    analyze_momentum()
    if data:
        manage_position(data[-1])
    time.sleep(60)


# Бэктестинг


# Запуск теста стратегии на данных за последние две недели
test_strategy_last_two_weeks()
