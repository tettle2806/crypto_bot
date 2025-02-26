import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover


class BollingerTrendStrategy(Strategy):
    fast_sma_period = 10
    slow_sma_period = 50
    bollinger_period = 20
    stop_loss = 0.02
    take_profit = 0.04

    def init(self):
        self.fast_sma = self.I(
            lambda x: pd.Series(x).rolling(self.fast_sma_period).mean(), self.data.Close
        )
        self.slow_sma = self.I(
            lambda x: pd.Series(x).rolling(self.slow_sma_period).mean(), self.data.Close
        )
        self.upper_band, self.middle_band, self.lower_band = self.I(
            self.calculate_bollinger_bands, self.data.Close
        )

    def calculate_bollinger_bands(self, close_prices):
        close_series = pd.Series(close_prices)
        sma = close_series.rolling(self.bollinger_period).mean()
        std = close_series.rolling(self.bollinger_period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return upper_band, sma, lower_band

    def next(self):
        if self.fast_sma[-1] > self.slow_sma[-1]:  # Восходящий тренд
            if self.data.Close[-1] < self.lower_band[-1]:
                print(f"Открываем LONG на {self.data.index[-1]}")
                self.buy(
                    size=1,
                    sl=self.data.Close[-1] * (1 - self.stop_loss),
                    tp=self.data.Close[-1] * (1 + self.take_profit),
                )

        elif self.fast_sma[-1] < self.slow_sma[-1]:  # Нисходящий тренд
            if self.data.Close[-1] > self.upper_band[-1]:
                print(f"Открываем SHORT на {self.data.index[-1]}")
                self.sell(
                    size=1,
                    sl=self.data.Close[-1] * (1 + self.stop_loss),
                    tp=self.data.Close[-1] * (1 - self.take_profit),
                )


# Функция для получения данных из Binance
import requests


def get_binance_data(symbol="BTCUSDT", interval="1h", limit=500):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(
        data,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df[["timestamp", "open", "high", "low", "close", "volume"]]


# Функция для расчета доходности
def calculate_performance(result):
    start_equity = result._equity_curve["Equity"].iloc[0]
    final_equity = result._equity_curve["Equity"].iloc[-1]
    return_percentage = (final_equity - start_equity) / start_equity * 100
    print(f"Доходность стратегии: {return_percentage:.2f}%")


# Запуск бэктеста
df = get_binance_data()
df.rename(
    columns={
        "timestamp": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    },
    inplace=True,
)
df.set_index("Date", inplace=True)

bt = Backtest(df, BollingerTrendStrategy, cash=100, margin=1 / 30)
result = bt.run()
bt.plot()

# Вывод доходности
calculate_performance(result)
