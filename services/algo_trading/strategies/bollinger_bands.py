import pandas as pd


def bollinger_bands_strategy(prices, window=20, num_std=2):
    df = pd.DataFrame(prices, columns=["price"])
    df["SMA"] = df["price"].rolling(window).mean()
    df["Upper"] = df["SMA"] + (df["price"].rolling(window).std() * num_std)
    df["Lower"] = df["SMA"] - (df["price"].rolling(window).std() * num_std)

    if df["price"].iloc[-1] <= df["Lower"].iloc[-1]:
        return "BUY"
    elif df["price"].iloc[-1] >= df["Upper"].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"