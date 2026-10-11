# NSE Signal Agent (research-only starter)

Rule-based NSE equity scanner with technical indicators, optional news sentiment,
multi-horizon scoring, ATR-based stop loss, configurable profit targets, Telegram
commands, and scheduled delivery. It does **not** execute trades.

## 1. Requirements
- Python 3.11+ recommended
- Telegram bot token from BotFather for Telegram features
- Internet access for Yahoo Finance / optional news API

## 2. Install
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```
Edit `.env`. Telegram variables may be blank if you only want CLI scans.

## 3. Run
```bash
python app.py --scan
python app.py --scan --symbols RELIANCE.NS,TCS.NS,INFY.NS
python app.py --bot
```

Telegram commands:
- `/start` — help
- `/scan` — run a scan
- `/scan RELIANCE.NS,TCS.NS` — scan selected tickers
- `/status` — configuration status

The bot's scheduled daily scan is enabled when `--bot` runs and Telegram credentials
are set. Schedule defaults are in `.env`; the default is 15:35 IST on weekdays.
This is a simple weekday schedule, not an authoritative NSE holiday calendar.

## Data and score interpretation
- Yahoo Finance data through `yfinance` is an unofficial convenience adapter and may
  be delayed, incomplete, rate-limited, or unavailable. Verify prices independently.
- Finnhub news is optional. If not configured or unavailable, sentiment is explicitly
  marked unavailable and the technical score remains usable.
- Scores are heuristic ranking scores, **not calibrated probabilities of profit**.
- T1–T4 default to +7%, +14%, +21%, +28% from entry; they are configurable in code.
- Stops use ATR and a risk floor. No target or stop is guaranteed to be reached.
- No automatic order placement is implemented.

## Important production hardening before relying on it
1. Replace the sample symbol list with a maintained, licensed NSE universe.
2. Use a licensed market-data source for any real-time or redistribution use.
3. Add the official NSE trading holiday calendar and verify session timestamps.
4. Backtest with point-in-time data, corporate actions, slippage, brokerage, taxes,
   survivorship-bias controls, and realistic entry/exit assumptions.
5. Add persistent caching, metrics, alert deduplication, deployment supervision, and
   integration tests before running unattended.
6. Restrict Telegram bot access with `TELEGRAM_CHAT_ID`; never expose the bot publicly
   without authorization checks.

This is software for educational research, not personalized investment advice.
