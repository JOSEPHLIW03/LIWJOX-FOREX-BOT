"""Research-only EUR/USD M15 baseline. No live or broker order execution."""
import csv
from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

LONDON=ZoneInfo("Europe/London"); NEW_YORK=ZoneInfo("America/New_York")
@dataclass
class Candle:
    timestamp: datetime; open: float; high: float; low: float; close: float
@dataclass
class Trade:
    side: str; entry_time: datetime; exit_time: datetime; entry: float; exit: float; stop: float; target: float; units: float; pnl: float; reason: str
def load_candles(path):
    out=[]
    with open(path,newline="",encoding="utf-8-sig") as f:
        r=csv.DictReader(f); required={"timestamp","open","high","low","close"}
        if not required.issubset(set(r.fieldnames or [])): raise ValueError("CSV requires timestamp,open,high,low,close")
        for row in r:
            ts=datetime.fromisoformat(row["timestamp"].replace("Z","+00:00"))
            if ts.tzinfo is None: raise ValueError("Timestamps must include timezone; UTC recommended")
            o,h,l,c=map(float,(row["open"],row["high"],row["low"],row["close"]))
            if min(o,h,l,c)<=0 or h<max(o,c,l) or l>min(o,c,h): raise ValueError("Invalid OHLC candle values")
            out.append(Candle(ts,o,h,l,c))
    out.sort(key=lambda x:x.timestamp)
    if any(out[i].timestamp==out[i-1].timestamp for i in range(1,len(out))): raise ValueError("Duplicate candle timestamps")
    return out
def ema(v,p):
    a=[None]*len(v)
    if len(v)<p:return a
    cur=sum(v[:p])/p;a[p-1]=cur;alpha=2/(p+1)
    for i in range(p,len(v)):cur=alpha*v[i]+(1-alpha)*cur;a[i]=cur
    return a
def rsi(v,p=14):
    out=[None]*len(v)
    if len(v)<=p:return out
    gains=[0.0]+[max(v[i]-v[i-1],0) for i in range(1,len(v))]
    losses=[0.0]+[max(v[i-1]-v[i],0) for i in range(1,len(v))]
    ag=sum(gains[1:p+1])/p;al=sum(losses[1:p+1])/p
    out[p]=100.0 if al==0 else 100-100/(1+ag/al)
    for i in range(p+1,len(v)):
        ag=(ag*(p-1)+gains[i])/p;al=(al*(p-1)+losses[i])/p
        out[i]=100.0 if al==0 else (0.0 if ag==0 else 100-100/(1+ag/al))
    return out
def atr(cs,p=14):
    out=[None]*len(cs)
    if len(cs)<=p:return out
    tr=[0.0]+[max(cs[i].high-cs[i].low,abs(cs[i].high-cs[i-1].close),abs(cs[i].low-cs[i-1].close)) for i in range(1,len(cs))]
    cur=sum(tr[1:p+1])/p;out[p]=cur
    for i in range(p+1,len(cs)):cur=(cur*(p-1)+tr[i])/p;out[i]=cur
    return out
def allowed_session(ts):
    l=ts.astimezone(LONDON).timetz().replace(tzinfo=None);n=ts.astimezone(NEW_YORK).timetz().replace(tzinfo=None)
    return time(8)<=l<time(16) or time(8)<=n<time(12)
def position_units(balance,risk,entry,stop):
    d=abs(entry-stop)
    if balance<=0 or risk<=0 or d<=0:return 0.0
    return balance*risk/d
def signal(i,cs,f,s,rs,ats):
    if any(a[i] is None for a in (f,s,rs,ats)) or not allowed_session(cs[i].timestamp):return "WAIT"
    if f[i]>s[i] and 52<=rs[i]<=68:return "BUY"
    if f[i]<s[i] and 32<=rs[i]<=48:return "SELL"
    return "WAIT"
def backtest(cs,starting_balance=1000.0,risk_fraction=0.005,daily_loss_limit_fraction=0.02):
    if starting_balance<=0:raise ValueError("Starting balance must be positive")
    if not 0<risk_fraction<=0.01:raise ValueError("Risk per trade must be >0 and <=1% in this prototype")
    if not 0<daily_loss_limit_fraction<=0.05:raise ValueError("Daily loss limit must be >0 and <=5%")
    if len(cs)<60:return [],[starting_balance]
    closes=[c.close for c in cs];f=ema(closes,20);s=ema(closes,50);rs=rsi(closes);ats=atr(cs)
    bal=starting_balance;curve=[bal];trades=[];active=None;day=None;day_start=bal
    for i in range(1,len(cs)):
        c=cs[i];d=c.timestamp.date()
        if d!=day:day=d;day_start=bal
        if active:
            side,ei,entry,stop,target,units=active
            hs=c.low<=stop if side=="BUY" else c.high>=stop
            ht=c.high>=target if side=="BUY" else c.low<=target
            if hs or ht:
                ex=stop if hs else target;pnl=(ex-entry)*units if side=="BUY" else (entry-ex)*units
                bal+=pnl;trades.append(Trade(side,cs[ei].timestamp,c.timestamp,entry,ex,stop,target,units,pnl,"SL" if hs else "TP"));active=None
        if (day_start-bal)/day_start>=daily_loss_limit_fraction:curve.append(bal);continue
        if active is None:
            sig=signal(i-1,cs,f,s,rs,ats);av=ats[i-1]
            if sig in ("BUY","SELL") and av and av>0:
                entry=c.open;dist=1.5*av;stop=entry-dist if sig=="BUY" else entry+dist;target=entry+2*dist if sig=="BUY" else entry-2*dist
                units=position_units(bal,risk_fraction,entry,stop)
                if units>0:active=(sig,i,entry,stop,target,units)
        curve.append(bal)
    if active:
        side,ei,entry,stop,target,units=active;last=cs[-1];ex=last.close;pnl=(ex-entry)*units if side=="BUY" else (entry-ex)*units;bal+=pnl
        trades.append(Trade(side,cs[ei].timestamp,last.timestamp,entry,ex,stop,target,units,pnl,"END_OF_DATA"));curve.append(bal)
    return trades,curve
def report(trades,curve,start):
    wins=[t for t in trades if t.pnl>0];loss=[t for t in trades if t.pnl<0];gp=sum(t.pnl for t in wins);gl=abs(sum(t.pnl for t in loss));peak=start;dd=0
    for e in curve:peak=max(peak,e);dd=max(dd,(peak-e)/peak if peak else 0)
    end=curve[-1] if curve else start;pf=gp/gl if gl else (float("inf") if gp else 0)
    return "\n".join(["LIWJOX RESEARCH-ONLY BACKTEST",f"Starting balance: ${start:,.2f}",f"Ending balance: ${end:,.2f}",f"Net P/L: ${end-start:,.2f}",f"Trades: {len(trades)}",f"Win rate: {100*len(wins)/len(trades):.1f}%" if trades else "Win rate: n/a (no trades)",f"Profit factor: {pf:.2f}",f"Max drawdown: {dd*100:.2f}%","LIMITATION: spread, commission, swaps, slippage, gaps and broker execution are not modeled.","Not a live-trading forecast; do not use to justify real-money trading."])
