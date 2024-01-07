from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, DateTime
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

    def add_trade_data(self, trade_data):
        self.data_buffer.append(trade_data)
        if len(self.data_buffer) >= 75:
            with self.engine.connect() as conn:
                conn.execute(self.trades.insert(), self.data_buffer)
                conn.commit()
            self.data_buffer.clear()