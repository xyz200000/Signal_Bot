from __future__ import annotations
import logging
import threading
import time
import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)
_cache: dict[str, tuple[float, pd.DataFrame]] = {}
_cache_lock = threading.Lock()

def fetch_ohlcv(symbol: str, period: str = "2y", ttl_seconds: int = 300) -> pd.DataFrame:
    """Fetch daily OHLCV. Raises ValueError for unusable data; never fabricates candles."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Empty symbol")
    key = f"{symbol}:{period}"
    now = time.time()
    with _cache_lock:
        cached = _cache.get(key)
        if cached and now - cached[0] < ttl_seconds:
            return cached[1].copy()

    frame = yf.download(
        symbol, period=period, interval="1d", auto_adjust=True,
        progress=False, threads=False, timeout=20
    )
    if frame is None or frame.empty:
        raise ValueError(f"No OHLCV returned for {symbol}")

    # yfinance may return MultiIndex columns even for one ticker.
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = [c[0] if isinstance(c, tuple) else c for c in frame.columns]
    frame.columns = [str(c).strip().title() for c in frame.columns]
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in frame.columns]
    if missing:
        raise ValueError(f"{symbol}: missing columns {missing}")

    frame = frame[required].copy()
    frame.index = pd.to_datetime(frame.index, errors="coerce")
    frame = frame.loc[~frame.index.isna()].sort_index()
    frame = frame[~frame.index.duplicated(keep="last")]
    frame = frame.apply(pd.to_numeric, errors="coerce")
    frame = frame.dropna(subset=["Open", "High", "Low", "Close"])
    frame = frame[(frame["Close"] > 0) & (frame["High"] >= frame["Low"])]
    if len(frame) < 60:
        raise ValueError(f"{symbol}: only {len(frame)} valid rows; need at least 60")
    with _cache_lock:
        _cache[key] = (now, frame.copy())
    return frame
