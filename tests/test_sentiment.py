from analysis.sentiment import score_news

def test_empty_news_is_unavailable_not_neutral():
    result = score_news([])
    assert result["score"] is None
    assert result["label"] == "UNAVAILABLE"

def test_headline_deduplication():
    articles = [
        {"headline": "Company beats estimates", "summary": ""},
        {"headline": " company   beats estimates ", "summary": ""},
    ]
    result = score_news(articles)
    assert result["article_count"] == 1
