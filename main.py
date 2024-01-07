import asyncio
import os
from dotenv import load_dotenv
import logging.config

from market_analysis import MarketAnalysis
from websocket_client import fetch_trades
from database_manager import DatabaseManager


logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URI = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}" \
               f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"


if __name__ == "__main__":
    db_manager = DatabaseManager(DATABASE_URI)

    analyzer = MarketAnalysis(db_manager)
    analyzer.analyze()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        fetch_trades('ethusdt', lambda data: db_manager.add_trade_data(data, logger), logger),
        fetch_trades('btcusdt', lambda data: db_manager.add_trade_data(data, logger), logger)))
