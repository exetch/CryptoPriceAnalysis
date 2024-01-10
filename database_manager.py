from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, DateTime, text
from sqlalchemy.exc import SQLAlchemyError


FETCHING_TIME_INTERVAL = 1
DELETING_TIME_INTERVAL = 1


class DatabaseManager:
    """
        Управление базой данных, включая добавление, извлечение и удаление торговых данных.

        Атрибуты:
        - engine: Объект движка SQLAlchemy для взаимодействия с базой данных.
        - metadata: Метаданные для определения структуры таблицы.
        - trades: Определение таблицы для хранения данных о торгах.
        - data_buffer: Буфер для временного хранения данных о торгах перед пакетной вставкой.
    """
    def __init__(self, uri):
        """
            Конструктор менеджера базы данных.

            Аргументы:
            - uri: строка подключения к базе данных.
        """
        self.engine = create_engine(uri)
        self.metadata = MetaData()
        self.trades = Table('trades', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('symbol', String),
                            Column('price', Float),
                            Column('quantity', Float),
                            Column('timestamp', DateTime))
        self.metadata.create_all(self.engine)
        self.data_buffer = []

    def add_trade_data(self, trade_data, logger):
        """
            Добавление данных о торгах в базу данных.

            Аргументы:
            - trade_data: данные о торгах для добавления.
            - logger: логгер для записи информационных сообщений и ошибок.
        """
        self.data_buffer.append(trade_data)
        if len(self.data_buffer) >= 100:
            try:
                with self.engine.connect() as conn:
                    conn.execute(self.trades.insert(), self.data_buffer)
                    conn.commit()
                logger.debug("Успешная вставка пакета данных размером %d", len(self.data_buffer))
            except SQLAlchemyError as e:
                logger.error("Ошибка при вставке данных: %s", e)
            finally:
                self.data_buffer.clear()

    def fetch_data(self, symbol):
        """
            Извлечение данных о торгах для указанного символа за последние 5 минут.

            Аргументы:
            - symbol: символ криптовалюты для извлечения данных.
        """
        with self.engine.begin() as conn:
            time_interval = datetime.now() - timedelta(days=FETCHING_TIME_INTERVAL)
            query = text(
                f"SELECT timestamp, price, quantity, symbol FROM trades WHERE symbol = '{symbol}' "
                f"AND timestamp >= '{time_interval}' ORDER BY timestamp ASC"
            )
            df = pd.read_sql_query(query, conn)
            df.sort_values(by='timestamp', inplace=True)
        return df

    def delete_old_data(self):
        """
            Удаление устаревших данных из базы данных (старше 1 часа).
        """
        with self.engine.begin() as conn:
            time_interval = datetime.now() - timedelta(days=DELETING_TIME_INTERVAL)
            query = text(
                f"DELETE FROM trades WHERE timestamp < '{time_interval}'")
            conn.execute(query)
