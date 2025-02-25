import unittest

import pandas as pd

from services.algo_trading.strategies.bollinger_bands import bollinger_bands_strategy, get_historical_prices
from services.algo_trading.strategies.macd import analyze_macd_rsi, macd_strategy, rsi_strategy
from services.algo_trading.strategies.sma import sma_strategy


class TestTradingStrategies(unittest.TestCase):
    def setUp(self):
        self.prices = pd.Series([i + (i % 5 - 2) for i in range(100)])  # Искусственные данные

    def test_macd_strategy(self):
        df_macd = macd_strategy(self.prices)
        self.assertIn("MACD", df_macd.columns)
        self.assertIn("Signal", df_macd.columns)

    def test_bollinger_bands_strategy(self):
        signal = bollinger_bands_strategy(self.prices)
        self.assertIn(signal, ["BUY", "SELL", "HOLD"])

    def test_rsi_strategy(self):
        rsi = rsi_strategy(self.prices)
        self.assertEqual(len(rsi), len(self.prices))

    def test_sma_strategy(self):
        signal = sma_strategy(self.prices)
        self.assertIn(signal, ["BUY", "SELL", "HOLD"])

    def test_analyze_macd_rsi(self):
        signal = analyze_macd_rsi()
        self.assertIn(signal, ["BUY", "SELL", "HOLD"])


if __name__ == "__main__":
    unittest.main()
