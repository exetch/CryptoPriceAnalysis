import asyncio
from telegram_bot import send_notification
from websocket_client import fetch_trades

async def fetch_data_forever(db_manager, logger):
    """
        Бесконечный асинхронный цикл для получения данных торгов с биржи.

        Аргументы:
        - db_manager: экземпляр DatabaseManager для работы с базой данных.
        - logger: экземпляр logger для логирования действий и ошибок.
    """
    while True:
        await asyncio.gather(
            fetch_trades('ethusdt', lambda data: db_manager.add_trade_data(data, logger), logger),
            fetch_trades('btcusdt', lambda data: db_manager.add_trade_data(data, logger), logger)
        )
        await asyncio.sleep(0.5)  # Короткая пауза


async def clean_old_data(db_manager, logger):
    """
        Бесконечный асинхронный цикл для регулярного удаления устаревших данных из базы данных.

        Аргументы:
        - db_manager: экземпляр DatabaseManager для работы с базой данных.
        - logger: экземпляр logger для логирования действий и ошибок.
    """
    while True:
        await asyncio.sleep(360)
        db_manager.delete_old_data()
        logger.info("Удаление устаревших данных...")


async def analyze_data_forever(logger, analyzer, strategy_name,sensitivity_level):
    """
    Бесконечный асинхронный цикл для анализа данных.
    """
    while True:
        result = analyzer.run_analysis()
        logger.info(f"{strategy_name} analysis result: {result}")
        if result is None:
            logger.warning(f"{strategy_name}: Недостаточно данных для анализа")
        elif result:
            actual_price, predicted_price, percentage_change = result
            if abs(percentage_change) > sensitivity_level:
                message = f"{strategy_name} - Фактическая цена ETH: {actual_price}, " \
                          f"Ожидаемая цена ETH: {predicted_price}, " \
                          f"Изменение цены ETH: {percentage_change}%"
                logger.warning(message)
                await send_notification(message)
        await asyncio.sleep(60)
