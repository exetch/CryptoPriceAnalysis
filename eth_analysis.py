from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor


class AnalysisStrategy(ABC):
    def prepare_data(self, df_eth, df_btc):
        # Агрегирование данных по минутам
        df_eth = df_eth.set_index('timestamp').resample('1T').mean(numeric_only=True).reset_index()
        df_btc = df_btc.set_index('timestamp').resample('1T').mean(numeric_only=True).reset_index()

        # Слияние данных ETH и BTC
        merged_data = pd.merge_asof(df_eth, df_btc, on='timestamp', suffixes=('_eth', '_btc'))

        # Добавление временных задержек для цен BTC
        for lag in range(1, 4):
            merged_data[f'lag_price_btc_{lag}'] = merged_data['price_btc'].shift(lag)

        # Удаление строк с NaN значениями
        merged_data.dropna(inplace=True)

        return merged_data

    @abstractmethod
    def analyze(self, df):
        pass

    @abstractmethod
    def predict(self, df, model):
        pass


class LinearRegressionStrategy(AnalysisStrategy):
    # def prepare_data(self, df_eth, df_btc):
    #     merged_data = pd.merge_asof(df_eth, df_btc, on='timestamp', suffixes=('_eth', '_btc'))
    #     merged_data.dropna(inplace=True)
    #     return merged_data

    def analyze(self, df):
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        X = sm.add_constant(df['price_btc'])
        y = df['price_eth']
        model = sm.OLS(y, X).fit()
        return model

    def predict(self, df, model):
        df['predicted_eth_price'] = model.predict(sm.add_constant(df['price_btc']))
        return df

class RandomForestStrategy(AnalysisStrategy):
    # def prepare_data(self, df_eth, df_btc):
    #     merged_data = pd.merge_asof(df_eth, df_btc, on='timestamp', suffixes=('_eth', '_btc'))
    #     merged_data.dropna(inplace=True)
    #     return merged_data

    def analyze(self, df):
        # Разделение данных на признаки и целевую переменную
        X = df[['price_btc']]
        y = df['price_eth']
        model = RandomForestRegressor()
        model.fit(X, y)
        return model

    def predict(self, df, model):
        # Добавление ожидаемой цены на ETH с поправкой на движение BTC
        df['predicted_eth_price'] = model.predict(df[['price_btc']])
        return df

class ETHPriceAnalysis:
    def __init__(self, db_manager, strategy: AnalysisStrategy):
        self.db_manager = db_manager
        self.strategy = strategy


    def run_analysis(self, symbol_eth='ETHUSDT', symbol_btc='BTCUSDT'):
        df_eth = self.db_manager.fetch_data(symbol_eth)
        df_btc = self.db_manager.fetch_data(symbol_btc)

        if df_eth.empty or df_btc.empty:
            return None

        df = self.strategy.prepare_data(df_eth, df_btc)
        model = self.strategy.analyze(df)
        df = self.strategy.predict(df, model)
        # Получить последнее наблюдение
        last_observation = df.iloc[-1]
        actual_price = round(last_observation['price_eth'], 2)
        predicted_price = round(last_observation['predicted_eth_price'], 2)
        percentage_change = round(((actual_price - predicted_price) / predicted_price) * 100, 2)

        return actual_price, predicted_price, percentage_change

    def calculate_cross_correlation(self, df):
        """
        Вычисление кросс-корреляции между ценами ETH и BTC.

        Аргументы:
        df -- DataFrame, содержащий объединенные данные ETH и BTC

        Возвращает:
        Серию значений кросс-корреляции.
        """
        df = df.sort_values(by='timestamp')
        # Вычисление кросс-корреляции
        lag_values = range(-10, 11)
        cross_corrs = [df['price_eth'].corr(df['price_btc'].shift(lag)) for lag in lag_values]
        return pd.Series(cross_corrs, index=lag_values)