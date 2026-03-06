from newsapi import NewsApiClient

API_KEY = "a7551c91dd7e4dc295a1d3dd259374a6"

newsapi = NewsApiClient(api_key=API_KEY)


def get_news(symbol):

    # remove .NS if present
    company = symbol.replace(".NS", "")

    news = newsapi.get_everything(
        q=company,
        language="en",
        sort_by="publishedAt",
        page_size=5
    )

    return news["articles"]