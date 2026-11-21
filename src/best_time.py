"""CLI examples (run from any folder):
  python src/best_time.py "Thika Road" in 5 --rain             day number: Sun=0 ... Sat=6
  python src/best_time.py "Thika Road" in 2026-12-11 --arrive-by 08:30
  python src/best_time.py "Mombasa Road" in 5 --erp --target 1.4"""
import argparse, datetime as dt, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src import model, planner
from src.calendar_ke import day_context
ap = argparse.ArgumentParser()
ap.add_argument("corridor"); ap.add_argument("direction", choices=["in", "out"])
ap.add_argument("day", help="0-6 (Sun=0) or a date YYYY-MM-DD")
ap.add_argument("--rain", action="store_true"); ap.add_argument("--arrive-by", metavar="HH:MM")
ap.add_argument("--erp", action="store_true"); ap.add_argument("--target", type=float, default=1.45)
a = ap.parse_args()
try:
    ctx = day_context(date=dt.date.fromisoformat(a.day), rain=a.rain) if "-" in a.day else day_context(dow=int(a.day), rain=a.rain)
    t = model.predict_day(a.corridor, a.direction, ctx)
except ValueError as e:
    sys.exit(f"Error: {e}")
fmt = lambda h: f"{h % 12 or 12}{'am' if h < 12 else 'pm'}"
print(f"{a.corridor} {a.direction}  {ctx}\nHour   typical  bad-day (p90)")
for h, r in t.iterrows(): print(f"{fmt(h):>5}  {r.p50:5.1f}   {r.p90:5.1f}   " + "#" * int(r.p50 / 3))
b = planner.best_time(t)
print(f"\nBest: {fmt(b['best_hour'])} ({b['best_minutes']:.0f} min)  Worst: {fmt(b['worst_hour'])} ({b['worst_minutes']:.0f} min)  Save up to {b['save_minutes']:.0f} min  (6am-8pm window)")
if a.arrive_by:
    h, m = map(int, a.arrive_by.split(":")); r = planner.leave_by(t, h * 60 + m)
    print(f"\nArrive by {r['arrive_by']}: " + (f"leave at {r['recommended']['leave_at']} (trip up to {r['recommended']['trip_minutes']:.0f} min). {r['message']}" if r["recommended"] else r["message"]))
if a.erp:
    e = planner.erp(t, model.bundle()["free"][a.corridor], a.target)
    print(f"\nRoad pricing to hold trips under {a.target}x free-flow:  peak KES {e['peak_price_kes']}, {e['hours_charged']} hours priced, ~{e['avg_minutes_saved']} min saved per remaining driver")
    for r in e["hours"]:
        if r["price_kes"]: print(f"{fmt(r['hour']):>5}  KES {r['price_kes']:>3}   {r['minutes_now']:.0f} -> {r['minutes_after']:.0f} min")
