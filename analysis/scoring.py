from __future__ import annotations
import math
import pandas as pd
from analysis.indicators import add_indicators

HORIZON_WEIGHTS = {
    "SHORT-TERM": {"trend": .25, "momentum": .30, "volume": .15, "return": .20, "sentiment": .10},
    "SWING":      {"trend": .35, "momentum": .20, "volume": .10, "return": .25, "sentiment": .10},
    "MID-TERM":   {"trend": .40, "momentum": .15, "volume": .05, "return": .30, "sentiment": .10},
}

def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))

def score_symbol(symbol: str, raw: pd.DataFrame, news: dict) -> dict:
    frame = add_indicators(raw)
    row = frame.iloc[-1]
    close = float(row["Close"])
    if not math.isfinite(close) or close <= 0:
        raise ValueError(f"{symbol}: invalid latest close")

    ema20, ema50, ema100 = (float(row[k]) for k in ("EMA20", "EMA50", "EMA100"))
    rsi = float(row["RSI"]) if pd.notna(row["RSI"]) else 50.0
    macd = float(row["MACD"]) if pd.notna(row["MACD"]) else 0.0
    macd_sig = float(row["MACD_SIGNAL"]) if pd.notna(row["MACD_SIGNAL"]) else 0.0
    atr = float(row["ATR"]) if pd.notna(row["ATR"]) else close * .03
    vol_sma = float(row["VOL_SMA20"]) if pd.notna(row["VOL_SMA20"]) else 0
    volume = float(row["Volume"]) if pd.notna(row["Volume"]) else 0
    ret20 = float(row["RETURN_20"]) if pd.notna(row["RETURN_20"]) else 0
    ret60 = float(row["RETURN_60"]) if pd.notna(row["RETURN_60"]) else 0

    trend = 100 if close > ema20 > ema50 else 70 if close > ema20 else 45 if close > ema50 else 20
    trend = min(100, trend + (10 if ema50 > ema100 else 0))
    momentum = 70 if 50 <= rsi <= 68 else 55 if 42 <= rsi < 50 else 45 if 68 < rsi <= 75 else 25 if rsi < 35 or rsi > 80 else 60
    momentum = _clamp(momentum + (15 if macd > macd_sig else -10))
    volume_score = 60 if vol_sma <= 0 else _clamp(50 + 25 * (volume / vol_sma - 1), 20, 90)
    ret_component = _clamp(50 + 250 * ret20, 0, 100)
    sentiment_score = None if news.get("score") is None else _clamp(50 + 50 * float(news["score"]))

    components = {
        "trend": trend, "momentum": momentum, "volume": volume_score,
        "return": _clamp(50 + 150 * ret20, 0, 100),
        "sentiment": sentiment_score,
    }
    scores = {}
    for horizon, weights in HORIZON_WEIGHTS.items():
        active = {k: w for k, w in weights.items() if k != "sentiment" or sentiment_score is not None}
        denominator = sum(active.values())
        scores[horizon] = round(sum(components[k] * w for k, w in active.items()) / denominator, 1)

    best_horizon = max(scores, key=scores.get)
    score = scores[best_horizon]
    # A score is a heuristic ranking score, not a probability.
    stop_distance = max(1.5 * atr, close * .025)
    stop_loss = max(0.01, close - stop_distance)
    targets = [close * (1 + pct) for pct in (.07, .14, .21, .28)]
    # Basic hard risk checks avoid issuing signals for obviously weak/invalid setups.
    eligible = score >= 0 and close > 0 and atr > 0
    action = "CONSIDER" if eligible and score >= 55 else "WATCH"
    if rsi >= 78:
        action = "WATCH"
    return {
        "symbol": symbol, "horizon": best_horizon, "score": score,
        "scores": scores, "action": action, "entry": close, "stop_loss": stop_loss,
        "targets": targets, "atr": atr, "rsi": rsi, "macd_bullish": macd > macd_sig,
        "news": news, "as_of": frame.index[-1].to_pydatetime(),
        "components": {"trend": round(trend, 1), "momentum": round(momentum, 1),
                       "volume": round(volume_score, 1), "return": round(ret_component, 1),
                       "sentiment": None if sentiment_score is None else round(sentiment_score, 1)},
    }
