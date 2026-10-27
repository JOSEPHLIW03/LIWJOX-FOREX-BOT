# Validation and release status

This is a source release candidate, not a production release.

- Backend unit tests are run locally before packaging.
- Android compilation has not been verified in this environment; use the GitHub Actions workflow and inspect its result.
- The Android Start/Pause control is UI-only.
- No real or demo broker is connected.
- No notification delivery service is connected.
- No genuine market data is included; sample CSV is header-only.
- Backtest ignores transaction costs and cannot establish profitability.
