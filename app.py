from __future__ import annotations
import argparse
import logging
from config import load_settings
from signals.generator import scan_symbols
from signals.formatter import format_digest

def main() -> None:
    parser = argparse.ArgumentParser(description="Rule-based NSE research signal scanner")
    parser.add_argument("--scan", action="store_true", help="run a one-off scan")
    parser.add_argument("--bot", action="store_true", help="start Telegram bot and scheduled scans")
    parser.add_argument("--symbols", help="comma-separated tickers, e.g. RELIANCE.NS,TCS.NS")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = load_settings()

    if args.scan or not args.bot:
        symbols = tuple(s.strip().upper() for s in args.symbols.split(",") if s.strip()) if args.symbols else settings.symbols
        results = scan_symbols(symbols, settings)
        print(format_digest(results))
    if args.bot:
        from delivery.telegram_bot import build_application
        app = build_application(settings)
        app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()
