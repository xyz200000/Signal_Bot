from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from config import Settings
from data.market_data import fetch_ohlcv
from data.news_data import fetch_finnhub_news
from analysis.sentiment import score_news
from analysis.scoring import score_symbol

log = logging.getLogger(__name__)

def scan_symbols(symbols: tuple[str, ...] | list[str], settings: Settings) -> list[dict]:
    results, failures = [], []
    def run(symbol: str):
        raw = fetch_ohlcv(symbol, settings.history_period, settings.cache_ttl_seconds)
        articles = fetch_finnhub_news(symbol, settings.finnhub_api_key, settings.news_lookback_hours)
        news = score_news(articles)
        return score_symbol(symbol, raw, news)
    with ThreadPoolExecutor(max_workers=settings.max_workers) as pool:
        futures = {pool.submit(run, s): s for s in symbols}
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                log.exception("Scan failed for %s", symbol)
                failures.append({"symbol": symbol, "error": str(exc)})
    results.sort(key=lambda x: x["score"], reverse=True)
    eligible = [r for r in results if r["action"] == "CONSIDER" and r["score"] >= settings.min_score]
    for r in eligible:
        r["scan_failures"] = failures
    return eligible[:settings.top_n]
