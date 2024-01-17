import asyncio
import os
from dotenv import load_dotenv
import logging.config
from async_tasks import fetch_data_forever, clean_old_data, analyze_data_forever
from eth_analysis import ETHPriceAnalysis, LinearRegressionStrategy, RandomForestStrategy
from database_manager import DatabaseManager
from telegram_bot import run_bot


# Инициализация логгера
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

# Загрузка переменных окружения и инициализация констант
load_dotenv()
DATABASE_URI = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}" \
               f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

LINEAR_REGRESSION = "Linear Regression"
RANDOM_FOREST ="Random Forest"
SENSITIVITY_LEVEL = 1

if __name__ == "__main__":
    # Создание экземпляров менеджера БД
    db_manager = DatabaseManager(DATABASE_URI)

    # Создание стратегий анализа (линейная регрессия и случайный лес)
    linear_regression_strategy = LinearRegressionStrategy()
    random_forest_strategy = RandomForestStrategy()
    linear_analyzer = ETHPriceAnalysis(db_manager, LinearRegressionStrategy())
    random_forest_analyzer = ETHPriceAnalysis(db_manager, RandomForestStrategy())

    # Получение цикла событий asyncio
    loop = asyncio.get_event_loop()
    # Создание задачи для запуска Telegram бота
    loop.create_task(run_bot())
    # Запуск асинхронных задач, включая получение данных, анализ и очистку данных
    loop.run_until_complete(asyncio.gather(
        fetch_data_forever(db_manager, logger),
        analyze_data_forever(logger, linear_analyzer, LINEAR_REGRESSION, SENSITIVITY_LEVEL),
        analyze_data_forever(logger, random_forest_analyzer, RANDOM_FOREST, SENSITIVITY_LEVEL),
        clean_old_data(db_manager, logger)
    ))
