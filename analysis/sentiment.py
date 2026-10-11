from __future__ import annotations
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

def score_news(articles: list[dict]) -> dict:
    """Return compound score in [-1, 1]. None means unavailable/no articles."""
    if not articles:
        return {"score": None, "article_count": 0, "label": "UNAVAILABLE"}
    # Deduplicate near-exact repeated headlines.
    seen, values = set(), []
    for article in articles:
        headline = " ".join(str(article.get("headline", "")).lower().split())
        if not headline or headline in seen:
            continue
        seen.add(headline)
        text = f"{article.get('headline', '')}. {article.get('summary', '')}".strip()
        values.append(_analyzer.polarity_scores(text)["compound"])
    if not values:
        return {"score": None, "article_count": 0, "label": "UNAVAILABLE"}
    score = sum(values) / len(values)
    label = "POSITIVE" if score >= 0.15 else "NEGATIVE" if score <= -0.15 else "MIXED/NEUTRAL"
    return {"score": score, "article_count": len(values), "label": label}
