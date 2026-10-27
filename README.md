# Liwjox Forex Bot — Full Project v1.0

A combined Android dashboard + research/demo backend starter for EUR/USD.

## Honest status
This package is source code, not a precompiled APK or a production-ready trading service. The Android project is intended to build through GitHub Actions. The Python backend is an offline research/simulation API only: it has no MT5/broker integration and cannot place real or demo broker orders. Push notifications, secure account onboarding, real market-data ingestion, broker execution, server deployment and operational monitoring still require implementation and security review.

## Safety defaults
- Research/paper mode only; no live-trading switch or broker credentials accepted.
- EUR/USD only.
- One open simulated position at a time.
- Risk per simulated trade capped at 0.5%; daily realised-loss limit 2%.
- SL and TP are simulated; gaps/slippage may cause worse real exits.
- No profit guarantee.

## Repository layout
- `android/` — native Kotlin + Jetpack Compose dashboard.
- `backend/` — Python standard-library signal/risk/backtest API and tests.
- `.github/workflows/android.yml` — cloud APK build workflow.

## Run backend tests
Python 3.10+:
```bash
cd backend
python -m unittest discover -s tests -v
```

## Run a backtest on real data
CSV must contain `timestamp,open,high,low,close` with timezone-aware ISO timestamps.
```bash
cd backend
python main.py --csv /path/to/EURUSD_M15.csv
```
Use licensed, genuine EUR/USD M15 data. This first backtest is educational and does not model broker costs, spread, slippage, swaps, or order rejection; results are not evidence of a profitable edge.

## Build Android APK using GitHub Actions
Upload the contents of this project to the root of your GitHub repository, preserving folders. Then open the repository's **Actions** tab and run **Build Liwjox Android APK** (or push to main). When successful, open the workflow run and download artifact `Liwjox-debug-apk`. GitHub account and internet access are required.

## Next engineering gates before any broker connection
1. Add real market data with timestamps/quality checks.
2. Model bid/ask spreads, commission, swaps, slippage and gaps in backtesting.
3. Use walk-forward and out-of-sample tests and publish full drawdown statistics.
4. Forward-test on a broker demo account.
5. Build a secure backend with authentication, encrypted secrets, audit logs, monitoring and kill switch.
6. Implement and independently validate a supported broker/MT5 execution adapter. Keep real-money mode disabled until explicit review.
