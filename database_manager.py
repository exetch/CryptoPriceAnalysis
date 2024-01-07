import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, DateTime, text
from sqlalchemy.exc import SQLAlchemyError


class DatabaseManager:
    def __init__(self, uri):
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
        self.data_buffer.append(trade_data)
        if len(self.data_buffer) >= 75:
            try:
                with self.engine.connect() as conn:
                    conn.execute(self.trades.insert(), self.data_buffer)
                    conn.commit()
                logger.info("Успешная вставка пакета данных размером %d", len(self.data_buffer))
            except SQLAlchemyError as e:
                logger.error("Ошибка при вставке данных: %s", e)
            finally:
                self.data_buffer.clear()

    def fetch_data(self, symbol):
        with self.engine.begin() as conn:
            query = text(
                f"SELECT timestamp, price, quantity, symbol FROM trades WHERE symbol = '{symbol}' ORDER BY timestamp ASC")
            df = pd.read_sql_query(query, conn)
            df.sort_values(by='timestamp', inplace=True)
        return df