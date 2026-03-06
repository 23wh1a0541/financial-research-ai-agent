import pandas as pd

def add_indicators(data):

    data["MA20"] = data["Close"].rolling(window=20).mean()
    data["MA50"] = data["Close"].rolling(window=50).mean()

    delta = data["Close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

    rs = gain / loss

    data["RSI"] = 100 - (100 / (1 + rs))

    return data