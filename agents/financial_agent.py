from services.stock_service import get_stock_data
from services.news_service import get_news
from services.sentiment_service import analyze_sentiment

def analyze_stock(symbol):

    data = get_stock_data(symbol)

    latest_price = data["Close"].iloc[-1]

    news = get_news(symbol)

    sentiments = []

    for article in news:

        title = article["title"]
        sentiment = analyze_sentiment(title)

        sentiments.append({
            "title": title,
            "sentiment": sentiment
        })

    return latest_price, sentiments