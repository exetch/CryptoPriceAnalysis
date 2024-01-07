import json
from datetime import datetime
import websockets

async def fetch_trades(symbol, callback):
    uri = f"wss://fstream.binance.com/ws/{symbol}@aggTrade"
    async with websockets.connect(uri) as ws:
        while True:
            data = await ws.recv()
            trade = json.loads(data)
            trade_data = {
                'symbol': trade['s'],
                'price': float(trade['p']),
                'quantity': float(trade['q']),
                'timestamp': datetime.fromtimestamp(trade['T'] / 1000.0)
            }
            callback(trade_data)
