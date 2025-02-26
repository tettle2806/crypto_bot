import requests
import time
import numpy as np
from binance.client import Client

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
ORDER_FLOW_THRESHOLD = 100  # Минимальный объем крупных рыночных ордеров

# Глобальные переменные
data = {"bids": [], "asks": [], "trades": []}
position = None
entry_price = 0


# Функция получения данных стакана и ленты принтов через REST API
def fetch_order_book():
    global data
    order_book = client.get_order_book(symbol=SYMBOL, limit=10)
    data["bids"] = [(float(price), float(qty)) for price, qty in order_book['bids']]
    data["asks"] = [(float(price), float(qty)) for price, qty in order_book['asks']]


def fetch_recent_trades():
    global data
    trades = client.get_recent_trades(symbol=SYMBOL, limit=100)
    data["trades"] = [(float(trade['price']), float(trade['qty']), trade['isBuyerMaker']) for trade in trades]


# Анализ дисбаланса ордеров
def analyze_order_flow():
    global position, entry_price
    buy_volume = sum(qty for price, qty, side in data["trades"] if not side)
    sell_volume = sum(qty for price, qty, side in data["trades"] if side)

    if buy_volume > ORDER_FLOW_THRESHOLD and not position:
        position = "long"
        entry_price = data["bids"][0][0]
        place_order("BUY")
    elif sell_volume > ORDER_FLOW_THRESHOLD and not position:
        position = "short"
        entry_price = data["asks"][0][0]
        place_order("SELL")


# Функция управления позицией
def manage_position(current_price):
    global position, entry_price
    if position:
        stop_loss_price = entry_price * (1 - STOP_LOSS / 100) if position == "long" else entry_price * (
                    1 + STOP_LOSS / 100)
        take_profit_price = entry_price * (1 + TAKE_PROFIT / 100) if position == "long" else entry_price * (
                    1 - TAKE_PROFIT / 100)

        if (position == "long" and (current_price <= stop_loss_price or current_price >= take_profit_price)) or \
                (position == "short" and (current_price >= stop_loss_price or current_price <= take_profit_price)):
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


# Основной цикл
while True:
    fetch_order_book()
    fetch_recent_trades()
    analyze_order_flow()
    if data["trades"]:
        manage_position(data["trades"][-1][0])
    time.sleep(1)


# Бэктестинг
def backtest(data):
    capital = 10000  # Начальный капитал
    balance = capital
    position = None
    entry_price = 0

    for price, qty, side in data["trades"]:
        if position is None:
            if qty > ORDER_FLOW_THRESHOLD and not side:
                position = "long"
                entry_price = price
            elif qty > ORDER_FLOW_THRESHOLD and side:
                position = "short"
                entry_price = price
        else:
            stop_loss_price = entry_price * (1 - STOP_LOSS / 100) if position == "long" else entry_price * (
                        1 + STOP_LOSS / 100)
            take_profit_price = entry_price * (1 + TAKE_PROFIT / 100) if position == "long" else entry_price * (
                        1 - TAKE_PROFIT / 100)

            if (position == "long" and (price <= stop_loss_price or price >= take_profit_price)) or \
                    (position == "short" and (price >= stop_loss_price or price <= take_profit_price)):
                profit = (take_profit_price - entry_price) if position == "long" else (entry_price - take_profit_price)
                balance += profit * QUANTITY
                position = None

    print(f"Конечный баланс: {balance}")
    return balance


# Пример запуска бэктеста
print(backtest(data=data))
