import numpy as np
import pandas as pd
import statsmodels.api as sm


class ETHPriceAnalysis:
    def __init__(self, db_manager):
        """
            Конструктор класса
        """
        self.db_manager = db_manager

    def prepare_data(self, df_eth, df_btc):
        """
            Слияние двух датафреймов по временным меткам.

            Аргументы:
            df_eth -- DataFrame содержащий данные по ETH
            df_btc -- DataFrame содержащий данные по BTC

            Возвращает:
            DataFrame, в котором каждая строка представляет собой слияние данных
            ETH и BTC по ближайшей временной метке.
        """
        merged_data = pd.merge_asof(df_eth, df_btc, on='timestamp', suffixes=('_eth', '_btc'))
        return merged_data
    def perform_regression_analysis(self, df):
        """
            Выполнение линейной регрессии для оценки влияния цен BTC на цены ETH.

            Аргументы:
            df -- DataFrame, содержащий объединенные данные ETH и BTC

            Возвращает:
            Модель линейной регрессии, описывающая зависимость цен ETH от цен BTC.
        """
        df = df.replace([np.inf, -np.inf], np.nan).dropna()  # Очистка данных
        X = sm.add_constant(df['price_btc'])
        y = df['price_eth']
        model = sm.OLS(y, X).fit()
        return model

    def calculate_predicted_eth_price(self, df, model):
        """
            Расчет предсказанных цен ETH на основе модели линейной регрессии.

            Аргументы:
            df -- DataFrame, содержащий данные для анализа
            model -- Модель линейной регрессии

            Возвращает:
            Обновленный DataFrame с добавленным столбцом предсказанных цен ETH.
        """
        df['predicted_eth_price'] = model.predict(sm.add_constant(df['price_btc']))
        return df

    def run_analysis(self, symbol_eth='ETHUSDT', symbol_btc='BTCUSDT'):
        """
            Запускает анализ данных, включая регрессию и расчет изменения цены.

            Аргументы:
            symbol_eth -- Символ для ETH.
            symbol_btc -- Символ для BTC.

            Возвращает:
            Фактическая цена ETH, предсказанная цена ETH и процентное изменение.
        """
        df_eth = self.db_manager.fetch_data(symbol_eth)
        df_btc = self.db_manager.fetch_data(symbol_btc)
        if df_eth.empty or df_btc.empty:
            return None
        df = self.prepare_data(df_eth, df_btc)
        model = self.perform_regression_analysis(df)
        self.calculate_predicted_eth_price(df, model)
        # Получить последнее наблюдение
        last_observation = df.iloc[-1]
        actual_price = last_observation['price_eth']
        predicted_price = last_observation['predicted_eth_price']
        percentage_change = round(((actual_price - predicted_price) / predicted_price) * 100, 2)

        return actual_price, predicted_price, percentage_change
