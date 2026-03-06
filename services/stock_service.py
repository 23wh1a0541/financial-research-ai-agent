import yfinance as yf


# -----------------------------
# GET STOCK PRICE DATA
# -----------------------------
def get_stock_data(symbol):

    stock = yf.Ticker(symbol)

    data = stock.history(period="6mo")

    return data


# -----------------------------
# GET FUNDAMENTAL DATA
# -----------------------------
def get_fundamentals(symbol):

    stock = yf.Ticker(symbol)

    info = stock.info

    return {
        "Market Cap": info.get("marketCap"),
        "PE Ratio": info.get("trailingPE"),
        "EPS": info.get("trailingEps"),
        "Revenue": info.get("totalRevenue")
    }