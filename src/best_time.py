"""CLI: python src/best_time.py "Thika Road" in 5 --rain
   (dow: Sun=0 ... Sat=6)"""
import argparse, joblib, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("corridor")
ap.add_argument("direction", choices=["in", "out"])
ap.add_argument("dow", type=int)
ap.add_argument("--rain", action="store_true")
a = ap.parse_args()

m = joblib.load("models/trip_model.joblib")
X = pd.DataFrame({"corridor": a.corridor, "direction": a.direction,
                  "hour": range(5, 23), "dow": a.dow, "rain": int(a.rain)})
X["pred"] = m.predict(X)

def fmt(h):
    return str(h % 12 or 12) + ("am" if h < 12 else "pm")

for _, r in X.iterrows():
    print(f"{fmt(int(r.hour)):>5}  {r.pred:5.1f} min  " + "#" * int(r.pred / 3))

b, w = X.loc[X.pred.idxmin()], X.loc[X.pred.idxmax()]
print(f"\nBest: {fmt(int(b.hour))} ({b.pred:.0f} min)   "
      f"Worst: {fmt(int(w.hour))} ({w.pred:.0f} min)   "
      f"Save up to {w.pred - b.pred:.0f} min")
