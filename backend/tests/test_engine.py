import os,sys,tempfile,unittest
from datetime import datetime,timezone
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from liwjox_engine import Candle,position_units,allowed_session,load_candles,backtest
class EngineTests(unittest.TestCase):
 def test_risk_sizing(self): self.assertAlmostEqual(position_units(1000,.005,1.1,1.095),1000)
 def test_invalid_sizing_is_zero(self): self.assertEqual(position_units(1000,.005,1.1,1.1),0)
 def test_session_timezone(self): self.assertTrue(allowed_session(datetime(2026,1,12,9,tzinfo=timezone.utc)))
 def test_naive_timestamp_rejected(self):
  with tempfile.NamedTemporaryFile(mode='w',delete=False) as f: f.write('timestamp,open,high,low,close\n2026-01-01T00:00:00,1,1.1,.9,1.01\n');name=f.name
  try:
   with self.assertRaises(ValueError): load_candles(name)
  finally: os.unlink(name)
 def test_bad_ohlc_rejected(self):
  with tempfile.NamedTemporaryFile(mode='w',delete=False) as f: f.write('timestamp,open,high,low,close\n2026-01-01T00:00:00Z,1,0.8,0.9,1.01\n');name=f.name
  try:
   with self.assertRaises(ValueError): load_candles(name)
  finally: os.unlink(name)
 def test_risk_caps_enforced(self):
  with self.assertRaises(ValueError): backtest([],1000,.02)
  with self.assertRaises(ValueError): backtest([],1000,.005,.10)
 def test_short_history_safe(self): self.assertEqual(backtest([],1000,.005)[0],[])
if __name__=='__main__': unittest.main()
