import unittest

import pandas as pd

from services.algo_trading.strategies.macd import macd_strategy, analyze_macd_rsi
from services.algo_trading.strategies.rsi import rsi_strategy


class TestTradingStrategies(unittest.TestCase):
    def setUp(self):
        self.prices = pd.Series([i + (i % 5 - 2) for i in range(100)])  # Искусственные данные

    def test_macd_strategy(self):
        df_macd = macd_strategy(self.prices)
        self.assertIn("MACD", df_macd.columns)
        self.assertIn("Signal", df_macd.columns)

    def test_rsi_strategy(self):
        rsi = rsi_strategy(self.prices)
        self.assertEqual(len(rsi), len(self.prices))

    def test_analyze_macd_rsi(self):
        signal = analyze_macd_rsi()
        self.assertIn(signal, ["BUY", "SELL", "HOLD"])