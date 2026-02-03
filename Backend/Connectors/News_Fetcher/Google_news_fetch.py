import feedparser
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

def clean_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def get_crypto_news(query: str, max_items: int = 5):
    encoded_query = quote_plus(query)

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    )

    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries[:max_items]:
        articles.append({
            "title": entry.title,
            "summary": clean_html(getattr(entry, "summary", "")),
            "link": entry.link,
            "published": getattr(entry, "published", None),
        })

    return articles

news = get_crypto_news("BTC OR Bitcoin OR BTCUSDT")
