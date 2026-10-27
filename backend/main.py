import argparse
from liwjox_engine import load_candles, backtest, report

def main():
    p = argparse.ArgumentParser(description="Liwjox EUR/USD research-only backtest")
    p.add_argument("--csv", required=True, help="Timezone-aware EUR/USD M15 OHLC CSV")
    p.add_argument("--balance", type=float, default=1000.0)
    p.add_argument("--risk", type=float, default=0.005)
    args = p.parse_args()
    candles = load_candles(args.csv)
    trades, equity = backtest(candles, args.balance, args.risk)
    print(report(trades, equity, args.balance))
if __name__ == "__main__": main()
