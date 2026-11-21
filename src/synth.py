"""SIMULATED trip-time generator. Replace data/trips.csv with real data (same columns) for a real project."""
import numpy as np, pandas as pd
from src.config import CORRIDORS, DATA
from src.calendar_ke import is_holiday, school_open
g = lambda h, c, w: np.exp(-((h - c) ** 2) / (2 * w * w))

def trip(free, a, m, h, d, direction, rain, holiday, school):
    wk = 0 < d < 6 and not holiday                      # holidays behave like weekends
    morn = g(h, 7.8, 1.1) * (1 if direction == "in" else .55) * (1 if school else .85)   # school run
    eve = g(h, 17.8, 1.4) * (1 if direction == "out" else .6)
    load = (morn + eve * (1.25 if d == 5 else 1.0) + .18 * g(h, 13, 1.5) * m) if wk else .35 * g(h, 12, 2.5) * (1.3 if d == 6 else .8)
    return free * (1 + a * load) * (1.28 + .35 * load if rain else 1)

def generate(path=DATA, weeks=52, seed=7):
    rng, rows = np.random.default_rng(seed), []
    for date in pd.date_range("2025-01-06", periods=weeks * 7):
        day, d, rain = date.date(), (date.dayofweek + 1) % 7, int(rng.random() < .25)
        hol, sch = int(is_holiday(day)), int(school_open(day))
        for name, (free, a, m) in CORRIDORS.items():
            for direction in ("in", "out"):
                for h in range(5, 23):
                    t = trip(free, a, m, h, d, direction, rain, hol, sch) * rng.lognormal(0, .08)
                    if rng.random() < .02: t *= rng.uniform(1.3, 2.0)      # rare incidents give heavy-tailed delays
                    rows.append([date, name, direction, h, d, rain, hol, sch, round(t, 1)])
    df = pd.DataFrame(rows, columns=["date", "corridor", "direction", "hour", "dow", "rain", "holiday", "school", "trip_min"])
    path.parent.mkdir(exist_ok=True); df.to_csv(path, index=False)
    return df
