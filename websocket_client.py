import json
from datetime import datetime
import websockets


async def fetch_trades(symbol, callback, logger):
    """
        Асинхронно получает торговые данные для заданного символа криптовалюты с использованием WebSocket.

        Эта функция подключается к WebSocket Binance, слушает торговые данные в реальном времени
        для указанного символа (например, 'ETHUSDT') и передаёт полученные данные в callback-функцию для дальнейшей обработки.

        Args:
            symbol (str): Символ криптовалюты, например 'ETHUSDT'.
            callback (function): Функция обратного вызова, которая обрабатывает полученные торговые данные.
            logger (Logger): Объект логгера для записи информационных сообщений и ошибок.

        Exceptions:
            Ошибки в работе WebSocket или при обработке данных логируются через logger.
    """
    try:
        uri = f"wss://fstream.binance.com/ws/{symbol}@aggTrade"
        logger.info("Подключение к WebSocket для %s", symbol)
        async with websockets.connect(uri) as ws:
            while True:
                data = await ws.recv()
                logger.info("Получены данные от %s: %s", symbol, data)
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

