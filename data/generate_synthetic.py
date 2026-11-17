"""Generate SYNTHETIC trip-time data for 6 Nairobi corridors (mirrors the dashboard model).
Replace data/trips.csv with real data (Uber Movement, Google Distance Matrix samples, GPS traces)."""
import numpy as np, pandas as pd
rng = np.random.default_rng(7)

COR = {"Thika Road": (32, 1.3, 1.0), "Mombasa Road": (35, 1.5, .9), "Waiyaki Way": (28, 1.1, 1.0),
       "Ngong Road": (26, 1.2, 1.1), "Jogoo Road": (22, 1.0, 1.2), "Limuru Road": (24, .9, .9)}
g = lambda h, c, w: np.exp(-((h - c) ** 2) / (2 * w * w))

def trip(free, a, m, h, d, direction, rain):
    wk = 0 < d < 6
    morn = g(h, 7.8, 1.1) * (1 if direction == "in" else .55)
    eve = g(h, 17.8, 1.4) * (1 if direction == "out" else .6)
    load = (morn + eve * (1.25 if d == 5 else 1.0) + .18 * g(h, 13, 1.5) * m) if wk \
        else .35 * g(h, 12, 2.5) * (1.3 if d == 6 else .8)
    rf = 1.28 + .35 * load if rain else 1
    return free * (1 + a * load) * rf

rows = []
for date in pd.date_range("2025-01-06", periods=26 * 7):
    rain = int(rng.random() < .25)          # rainy day flag
    d = (date.dayofweek + 1) % 7            # Sun=0 ... Sat=6
    for name, (free, a, m) in COR.items():
        for direction in ("in", "out"):
            for h in range(5, 23):
                t = trip(free, a, m, h, d, direction, rain)
                t *= rng.lognormal(0, .08)   # real-world noise
                rows.append([date, name, direction, h, d, rain, round(t, 1)])
pd.DataFrame(rows, columns=["date", "corridor", "direction", "hour", "dow", "rain", "trip_min"]).to_csv("data/trips.csv", index=False)
print("wrote data/trips.csv", len(rows), "rows")
