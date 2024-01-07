import numpy as np
import pandas as pd
import statsmodels.api as sm


class ETHPriceAnalysis:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def prepare_data(self, df_eth, df_btc):
        df = pd.merge_asof(df_eth, df_btc, on='timestamp', suffixes=('_eth', '_btc'))
        df = df.dropna()
        return df
    def perform_regression_analysis(self, df):
        X = sm.add_constant(df['price_btc'])
        y = df['price_eth']
        model = sm.OLS(y, X).fit()
        return model

    def calculate_residuals(self, df, model):
        df['predicted_eth_price'] = model.predict(sm.add_constant(df['price_btc']))
        df['residuals'] = df['price_eth'] - df['predicted_eth_price']
        return df['residuals']

    def run_analysis(self, symbol_eth='ETHUSDT', symbol_btc='BTCUSDT'):
        df_eth = self.db_manager.fetch_data(symbol_eth)
        df_btc = self.db_manager.fetch_data(symbol_btc)
        if df_eth.empty or df_btc.empty:
            return None
        df = self.prepare_data(df_eth, df_btc)
        model = self.perform_regression_analysis(df)
        self.calculate_residuals(df, model)
        # Получить последнее наблюдение
        last_observation = df.iloc[-1]
        actual_price = last_observation['price_eth']
        predicted_price = last_observation['predicted_eth_price']
        percentage_change = ((actual_price - predicted_price) / predicted_price) * 100

        return actual_price, predicted_price, percentage_change
