from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def format_signal(signal: dict) -> str:
    entry = signal["entry"]
    targets = signal["targets"]
    news = signal["news"]
    news_text = "N/A" if news.get("score") is None else f"{news['score']:+.2f} ({news['label']})"
    as_of = signal["as_of"]
    if as_of.tzinfo is None:
        # Daily Yahoo data index is usually exchange-local-naive; label as date only.
        as_of_text = as_of.strftime("%d %b %Y")
    else:
        as_of_text = as_of.astimezone(IST).strftime("%d %b %Y")
    lines = [
        f"{signal['symbol']} – {signal['action']} ({signal['score']:.1f}/100)",
        f"Horizon: {signal['horizon']}",
        f"Data date: {as_of_text}",
        f"Entry reference: ₹{entry:,.2f}",
    ]
    for i, target in enumerate(targets, start=1):
        pct = (target / entry - 1) * 100
        lines.append(f"T{i}: ₹{target:,.2f} (+{pct:.0f}%)")
    sl_pct = (signal["stop_loss"] / entry - 1) * 100
    lines.append(f"SL: ₹{signal['stop_loss']:,.2f} ({sl_pct:.1f}%)")
    lines.append(
        "Scores: " + " ".join(f"{k.title()} {v:.0f}" for k, v in signal["scores"].items())
    )
    lines.append(
        f"RSI: {signal['rsi']:.1f} | News: {news_text} | Articles: {news.get('article_count', 0)}"
    )
    lines.append(f"Generated: {datetime.now(IST).strftime('%d %b %Y, %I:%M %p IST')}")
    lines.append("Research signal only — verify live prices; not a trade instruction.")
    return "\n".join(lines)

def format_digest(signals: list[dict]) -> str:
    if not signals:
        return "NSE Signal Agent\nNo signals passed the configured score threshold.\nResearch only."
    blocks = [format_signal(s) for s in signals]
    # Telegram limit is 4096 chars; split is handled by delivery caller.
    return "\n\n".join(blocks)
