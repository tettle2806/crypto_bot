import asyncio
import json
import websockets
import requests

# Пара для анализа
SYMBOL = "btcusdt"
DEPTH_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL}@depth"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

# Порог для детекции айсберг-заявок
ICEBERG_THRESHOLD = 5

# Кэш для хранения объемов заявок
order_book = {}

async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, json=payload)

async def detect_iceberg(level, new_volume):
    """ Проверка аномального появления/исчезновения ордеров """
    old_volume = order_book.get(level, 0)
    change = abs(new_volume - old_volume)
    if change >= ICEBERG_THRESHOLD:
        await send_telegram_message(f"🚨 Обнаружен айсберг-заявка на уровне {level}: объем {new_volume}")
    order_book[level] = new_volume

async def process_depth_update(data):
    """ Обработка обновлений стакана """
    for bid in data.get("b", []):  # Покупки (bid)
        price, volume = float(bid[0]), float(bid[1])
        await detect_iceberg(price, volume)
    for ask in data.get("a", []):  # Продажи (ask)
        price, volume = float(ask[0]), float(ask[1])
        await detect_iceberg(price, volume)

async def listen_to_depth():
    """ Подключение к WebSocket Binance """
    async with websockets.connect(DEPTH_URL) as ws:
        while True:
            response = await ws.recv()
            data = json.loads(response)
            await process_depth_update(data)

if __name__ == "__main__":
    asyncio.run(listen_to_depth())
