from __future__ import annotations
from datetime import datetime, timedelta, timezone
import logging
import requests

log = logging.getLogger(__name__)
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "NSESignalAgent/1.0 (research)"})

def fetch_finnhub_news(symbol: str, api_key: str, lookback_hours: int = 72) -> list[dict]:
    """Optional Finnhub company news. Empty list means no usable articles, not neutral news."""
    if not api_key:
        return []
    # Strip common Yahoo suffix for the company-news symbol query.
    ticker = symbol.upper().removesuffix(".NS").removesuffix(".BO")
    end = datetime.now(timezone.utc).date()
    start = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).date()
    try:
        response = SESSION.get(
            "https://finnhub.io/api/v1/company-news",
            params={"symbol": ticker, "from": start.isoformat(), "to": end.isoformat(), "token": api_key},
            timeout=12,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return []
        cutoff = datetime.now(timezone.utc).timestamp() - lookback_hours * 3600
        out = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            ts = item.get("datetime")
            if isinstance(ts, (int, float)) and ts < cutoff:
                continue
            headline = str(item.get("headline", "")).strip()
            summary = str(item.get("summary", "")).strip()
            if headline:
                out.append({
                    "headline": headline, "summary": summary,
                    "url": item.get("url", ""), "timestamp": ts,
                    "source": item.get("source", "Finnhub"),
                })
        return out
    except (requests.RequestException, ValueError, TypeError) as exc:
        log.warning("Finnhub news unavailable for %s: %s", symbol, exc)
        return []
