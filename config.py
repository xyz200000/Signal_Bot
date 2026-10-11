from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default

@dataclass(frozen=True)
class Settings:
    symbols: tuple[str, ...]
    top_n: int
    history_period: str
    news_lookback_hours: int
    min_score: float
    scan_interval_minutes: int
    schedule_hour_ist: int
    schedule_minute_ist: int
    max_workers: int
    cache_ttl_seconds: int
    telegram_bot_token: str
    telegram_chat_id: str
    finnhub_api_key: str
    newsapi_key: str

def load_settings() -> Settings:
    symbols = tuple(
        s.strip().upper() for s in os.getenv(
            "SYMBOLS",
            "RELIANCE.NS,TCS.NS,INFY.NS,HDFCBANK.NS,ICICIBANK.NS"
        ).split(",") if s.strip()
    )
    return Settings(
        symbols=symbols,
        top_n=max(1, _int("TOP_N", 10)),
        history_period=os.getenv("HISTORY_PERIOD", "2y"),
        news_lookback_hours=max(1, _int("NEWS_LOOKBACK_HOURS", 72)),
        min_score=float(os.getenv("MIN_SCORE", "55")),
        scan_interval_minutes=max(5, _int("SCAN_INTERVAL_MINUTES", 60)),
        schedule_hour_ist=min(23, max(0, _int("SCHEDULE_HOUR_IST", 15))),
        schedule_minute_ist=min(59, max(0, _int("SCHEDULE_MINUTE_IST", 35))),
        max_workers=min(16, max(1, _int("MAX_WORKERS", 4))),
        cache_ttl_seconds=max(0, _int("CACHE_TTL_SECONDS", 300)),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        finnhub_api_key=os.getenv("FINNHUB_API_KEY", "").strip(),
        newsapi_key=os.getenv("NEWSAPI_KEY", "").strip(),
    )
