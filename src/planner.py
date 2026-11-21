"""Decision tools on top of the model. Singapore-style ideas: reliability buffers, arrive-by planning,
congestion pricing (ERP) and incident detection (EMAS)."""
import math
hm = lambda m: f"{m // 60:02d}:{m % 60:02d}"

def best_time(t, lo=6, hi=20):
    """Best/worst departure inside the commuting window (the old version said '10pm', which nobody commutes at)."""
    w = t.loc[lo:hi]; b, x = w.p50.idxmin(), w.p50.idxmax()
    return dict(window=[lo, hi], best_hour=int(b), best_minutes=round(w.p50[b], 1), worst_hour=int(x), worst_minutes=round(w.p50[x], 1),
                save_minutes=round(w.p50[x] - w.p50[b], 1), buffer_index=round(float(((w.p90 - w.p50) / w.p50).mean()), 3),
                hourly={int(h): round(r.p50, 1) for h, r in t.iterrows()}, hourly_p90={int(h): round(r.p90, 1) for h, r in t.iterrows()})

def leave_by(t, arrive_min):
    """Latest departure that still arrives on time: on a typical day (p50) and with a reliability buffer (p90)."""
    def latest(col):
        for d in range(t.index.max() * 60 + 55, t.index.min() * 60 - 1, -5):
            if d + t[col][d // 60] <= arrive_min: return d
    a, b = latest("p50"), latest("p90")
    f = lambda d: None if d is None else dict(leave_at=hm(d), trip_minutes=round(float(t.p90[d // 60] if d is b else t.p50[d // 60]), 1))
    return dict(arrive_by=hm(arrive_min), recommended=f(b), typical_day=f(a),
                buffer_minutes=None if a is None or b is None else a - b,
                message="Leave at the recommended time to arrive on time on 9 days out of 10." if b is not None else "Cannot arrive by then, even leaving at 05:00.")

def erp(t, free, target=1.45, elasticity=-.25, step=10, cap=300):
    """Price per departure hour that keeps trips under target x free-flow time.
    Assumption: demand falls by |elasticity| per KES 100 (measure the real value before use) and delay scales with demand."""
    rows = []
    for h, r in t.iterrows():
        ci, price = r.p50 / free, 0
        if ci > target:
            need = (target - 1) / (ci - 1)                       # share of demand that may stay
            price = min(cap, math.ceil((1 - need) / abs(elasticity) * 100 / step) * step)
        keep = max(.3, 1 + elasticity * price / 100)
        rows.append(dict(hour=int(h), congestion=round(ci, 2), price_kes=int(price), minutes_now=round(r.p50, 1),
                         minutes_after=round(free * (1 + (ci - 1) * keep), 1), demand_shifted_pct=round((1 - keep) * 100)))
    paid = [r for r in rows if r["price_kes"]]
    return dict(target=target, elasticity=elasticity, hours=rows, hours_charged=len(paid), peak_price_kes=max([r["price_kes"] for r in rows]),
                avg_minutes_saved=round(sum(r["minutes_now"] - r["minutes_after"] for r in paid) / len(paid), 1) if paid else 0)

def check_reading(t, hour, observed):
    """Compare a live trip time with what is expected for that hour."""
    p50, p90 = float(t.p50[hour]), float(t.p90[hour])
    s = "normal" if observed <= p90 else "slower_than_usual" if observed <= p90 * 1.25 else "possible_incident"
    return dict(status=s, observed=observed, expected=round(p50, 1), p90=round(p90, 1), extra_minutes=round(observed - p50, 1), ratio=round(observed / p50, 2))
