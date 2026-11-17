"""Train a gradient-boosting regressor to predict trip minutes. Time-based test split."""
import joblib, numpy as np, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

CAT, NUM = ["corridor", "direction"], ["hour", "dow", "rain"]
df = pd.read_csv("data/trips.csv", parse_dates=["date"])
cut = df.date.max() - pd.Timedelta(weeks=6)
tr, te = df[df.date <= cut], df[df.date > cut]

def build(model):
    pre = ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore"), CAT)], remainder="passthrough")
    return make_pipeline(pre, model)

def fit_eval(name, model):
    m = build(model).fit(tr[CAT + NUM], tr.trip_min)
    p = m.predict(te[CAT + NUM])
    print(f"{name:<24} MAE={mean_absolute_error(te.trip_min, p):5.2f} min   R2={r2_score(te.trip_min, p):.3f}")
    return m

print(f"Train rows: {len(tr)}   Test rows (last 6 weeks): {len(te)}")
fit_eval("Ridge (baseline)", Ridge())
gb = fit_eval("Gradient boosting", HistGradientBoostingRegressor(max_iter=300, learning_rate=.08, random_state=0))
joblib.dump(gb, "models/trip_model.joblib")
print("Saved models/trip_model.joblib")
