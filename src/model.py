"""Train, save, load and use the trip-time models: median (p50) and 'plan for it' (p90)."""
import functools, joblib, numpy as np, pandas as pd, sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor as HGB
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_pinball_loss, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from src.config import CAT, CORRIDORS, DATA, HOURS, MODEL, NUM
SCHEMA = 2   # bump when features change so old saved models are rebuilt

def _build(est):
    return make_pipeline(ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore"), CAT)], remainder="passthrough"), est)
_q = lambda q: _build(HGB(loss="quantile", quantile=q, max_iter=200, learning_rate=.1, random_state=0))
X = lambda d: d[CAT + NUM]

def train(verbose=True):
    if not DATA.exists():
        from src.synth import generate; generate()
    df = pd.read_csv(DATA, parse_dates=["date"])
    tr, te = df[df.date <= df.date.max() - pd.Timedelta(weeks=8)], df[df.date > df.date.max() - pd.Timedelta(weeks=8)]
    key = ["corridor", "direction", "hour", "dow"]
    hist = te.merge(tr.groupby(key).trip_min.mean().rename("h").reset_index(), how="left", on=key).h.fillna(tr.trip_min.mean())
    ridge = _build(Ridge()).fit(X(tr), tr.trip_min).predict(X(te))
    p50 = _q(.5).fit(X(tr), tr.trip_min).predict(X(te)); p90 = np.maximum(_q(.9).fit(X(tr), tr.trip_min).predict(X(te)), p50)
    m = {"rows_train": len(tr), "rows_test": len(te), "mae_historical_average": round(mean_absolute_error(te.trip_min, hist), 2),
         "mae_ridge": round(mean_absolute_error(te.trip_min, ridge), 2), "mae_p50": round(mean_absolute_error(te.trip_min, p50), 2),
         "r2_p50": round(r2_score(te.trip_min, p50), 3), "p90_coverage": round(float((te.trip_min <= p90).mean()), 3),
         "p90_pinball": round(mean_pinball_loss(te.trip_min, p90, alpha=.9), 2)}
    if verbose:
        print(f"Train rows: {m['rows_train']}   Test rows (last 8 weeks): {m['rows_test']}")
        print(f"Historical average       MAE={m['mae_historical_average']:5.2f} min   (what a simple lookup table gives)")
        print(f"Ridge (baseline)         MAE={m['mae_ridge']:5.2f} min")
        print(f"Gradient boosting (p50)  MAE={m['mae_p50']:5.2f} min   R2={m['r2_p50']:.3f}")
        print(f"p90 'plan for it' model  covers {m['p90_coverage']*100:.1f}% of trips (target 90%)")
    full = {"p50": _q(.5).fit(X(df), df.trip_min), "p90": _q(.9).fit(X(df), df.trip_min)}   # production models use all data
    b = dict(full, sklearn=sklearn.__version__, schema=SCHEMA, metrics=m, free={})
    for c in CORRIDORS:                                    # free-flow = quickest typical dry weekday trip
        Xc = pd.DataFrame({"corridor": c, "direction": ["in", "out"] * len(HOURS), "hour": [h for h in HOURS for _ in (0, 1)], "dow": 2, "rain": 0, "holiday": 0, "school": 1})
        b["free"][c] = float(b["p50"].predict(Xc).min())
    MODEL.parent.mkdir(exist_ok=True); joblib.dump(b, MODEL)
    return b

_B = None
def bundle():
    """Load the saved model; retrain automatically if missing or built by a different scikit-learn."""
    global _B
    if _B is None:
        try:
            _B = joblib.load(MODEL) if MODEL.exists() else None
            if _B and (_B.get("sklearn") != sklearn.__version__ or _B.get("schema") != SCHEMA): _B = None
        except Exception: _B = None
        if _B is None:
            print("Saved model missing or from another scikit-learn version: training a new one (about 20 s)...")
            _B = train(verbose=False)
    return _B

def check_inputs(corridor, direction):
    if corridor not in CORRIDORS: raise ValueError(f"Unknown corridor '{corridor}'. Choose from: {', '.join(CORRIDORS)}")
    if direction not in ("in", "out"): raise ValueError("direction must be 'in' or 'out'")

@functools.lru_cache(maxsize=4096)
def _pred(c, d, dow, rain, hol, sch):
    b, hrs = bundle(), list(HOURS)
    Xd = pd.DataFrame({"corridor": c, "direction": d, "hour": hrs, "dow": dow, "rain": rain, "holiday": hol, "school": sch})
    p50 = b["p50"].predict(Xd)
    return tuple(p50), tuple(np.maximum(b["p90"].predict(Xd), p50))

def predict_day(corridor, direction, ctx):
    """Hourly table indexed by departure hour with columns p50 (typical) and p90 (bad day)."""
    check_inputs(corridor, direction)
    p50, p90 = _pred(corridor, direction, ctx["dow"], ctx["rain"], ctx["holiday"], ctx["school"])
    return pd.DataFrame({"hour": list(HOURS), "p50": p50, "p90": p90}).set_index("hour")
