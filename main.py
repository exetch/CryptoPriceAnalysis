import asyncio
from websocket_client import fetch_trades
from database_manager import DatabaseManager
import os
from dotenv import load_dotenv
import logging
import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URI = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

def process_trade_data(trade_data, db_manager):
    try:
        db_manager.add_trade_data(trade_data)
    except Exception as e:
        logger.error("Ошибка при работе с базой данных: %s", e)

if __name__ == "__main__":
    db_manager = DatabaseManager(DATABASE_URI)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        fetch_trades('ethusdt', lambda data: process_trade_data(data, db_manager)),
        fetch_trades('btcusdt', lambda data: process_trade_data(data, db_manager))))


