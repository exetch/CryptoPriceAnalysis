import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
import statsmodels.api as sm

class MarketAnalysis:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)

    def fetch_data(self, symbol):
        with self.engine.begin() as conn:
            query = text(f"SELECT timestamp, price, quantity, symbol FROM trades WHERE symbol = '{symbol}' ORDER BY timestamp ASC")
            df = pd.read_sql_query(query, conn)
        return df

    def prepare_data(self, df_eth, df_btc):
        df = pd.merge_asof(df_eth, df_btc, on='timestamp', suffixes=('_eth', '_btc'))
        df = df.dropna()
        print(df)
        return df

    def calculate_correlation(self, df):
        correlation = df['price_eth'].corr(df['price_btc'])
        return correlation

    def perform_regression(self, df):
        if df.empty or df['price_btc'].isnull().all() or df['price_eth'].isnull().all():
            return "Недостаточно данных для регрессионного анализа"
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        X = df[['price_btc']]
        y = df['price_eth']
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        return model.summary()

    def analyze(self, symbol_eth='ETHUSDT', symbol_btc='BTCUSDT'):
        df_eth = self.fetch_data(symbol_eth).sort_values(by='timestamp')
        df_btc = self.fetch_data(symbol_btc).sort_values(by='timestamp')
        df = self.prepare_data(df_eth, df_btc)
        print("Correlation:", self.calculate_correlation(df))
        print("Regression:\n", self.perform_regression(df))




