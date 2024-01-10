import ccxt
import pandas as pd
from sqlalchemy import create_engine
import os


exchange = ccxt.binance({
    'apiKey': os.getenv('api_key'),
    'secret': os.getenv('secret_key'),
    'enableRateLimit': True,
})
DATABASE_URI = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}" \
               f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URI)

def fetch_and_save_historical_data(symbol, timeframe, since, limit=1000):
    while True:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        df.to_sql(symbol.replace('/', '_'), engine, if_exists='append', index=False)

        if len(ohlcv) < limit:
            break
        since = ohlcv[-1][0] + 1

if __name__ == "__main__":
    fetch_and_save_historical_data('BTC/USDT', '1m', exchange.parse8601('2022-01-01T00:00:00Z'))

