from textblob import TextBlob

def analyze_sentiment(news):

    positive = 0
    negative = 0
    neutral = 0

    for article in news:

        text = article["title"]

        analysis = TextBlob(text)

        score = analysis.sentiment.polarity

        if score > 0:
            positive += 1
        elif score < 0:
            negative += 1
        else:
            neutral += 1

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral
    }