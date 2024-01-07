import asyncio
import os
from dotenv import load_dotenv
import logging.config
from eth_analysis import ETHPriceAnalysis
from websocket_client import fetch_trades
from database_manager import DatabaseManager


logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URI = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}" \
               f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"


async def fetch_data_forever():
    while True:
        await asyncio.gather(
            fetch_trades('ethusdt', lambda data: db_manager.add_trade_data(data, logger), logger),
            fetch_trades('btcusdt', lambda data: db_manager.add_trade_data(data, logger), logger)
        )
        await asyncio.sleep(0.5)  # Короткая пауза

async def clean_old_data():
    while True:
        await asyncio.sleep(360)
        db_manager.delete_old_data()
        logger.info("Удаление устаревших данных...")

async def analyze_data_forever():
    while True:
        result = analyzer.run_analysis()
        print(result)
        if result is None:
            logger.info("Недостаточно данных для анализа")
        if result:
            actual_price, predicted_price, percentage_change = result
            if abs(percentage_change) > 0.1:
                print(
                    f"Фактическая цена ETH: {actual_price}"
                    f"Ожидаемая цена ETH c учетом движения BTC: {predicted_price}"
                    f"Собственное изменение цены ETH: {percentage_change}%")
        await asyncio.sleep(60)

if __name__ == "__main__":
    db_manager = DatabaseManager(DATABASE_URI)
    analyzer = ETHPriceAnalysis(db_manager)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        fetch_data_forever(),
        analyze_data_forever(),
        clean_old_data()
    ))
