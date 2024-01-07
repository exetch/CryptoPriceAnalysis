import json
from datetime import datetime
import websockets


async def fetch_trades(symbol, callback, logger):
    try:
        uri = f"wss://fstream.binance.com/ws/{symbol}@aggTrade"
        logger.info("Подключение к WebSocket для %s", symbol)
        async with websockets.connect(uri) as ws:
            while True:
                data = await ws.recv()
                logger.debug("Получены данные от %s: %s", symbol, data)
                trade = json.loads(data)
                trade_data = {
                    'symbol': trade['s'],
                    'price': float(trade['p']),
                    'quantity': float(trade['q']),
                    'timestamp': datetime.fromtimestamp(trade['T'] / 1000.0)
                }
                callback(trade_data)
    except Exception as e:
        logger.error("Ошибка при подключении к WebSocket для %s: %s", symbol, e)

