import asyncio
import os
from dotenv import load_dotenv
import logging.config
from async_tasks import fetch_data_forever, clean_old_data, analyze_data_forever
from eth_analysis import ETHPriceAnalysis
from database_manager import DatabaseManager

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URI = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}" \
               f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

if __name__ == "__main__":
    db_manager = DatabaseManager(DATABASE_URI)
    analyzer = ETHPriceAnalysis(db_manager)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        fetch_data_forever(db_manager, logger),
        analyze_data_forever(logger, analyzer),
        clean_old_data(db_manager, logger)
    ))
