import numpy as np
import pandas as pd
import statsmodels.api as sm


class MarketAnalysis:
    def __init__(self, db_manager):
        self.db_manager = db_manager


    def prepare_data(self, df_eth, df_btc):
        df = pd.merge_asof(df_eth, df_btc, on='timestamp', suffixes=('_eth', '_btc'))
        df = df.dropna()
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
        df_eth = self.db_manager.fetch_data(symbol_eth)
        df_btc = self.db_manager.fetch_data(symbol_btc)
        df = self.prepare_data(df_eth, df_btc)
        print("Correlation:", self.calculate_correlation(df))
        print("Regression:\n", self.perform_regression(df))
