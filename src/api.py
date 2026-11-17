"""Run: uvicorn src.api:app --reload   then open http://127.0.0.1:8000/docs"""
import joblib, pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="NairobiMove API")
model = joblib.load("models/trip_model.joblib")

class Trip(BaseModel):
    corridor: str = "Thika Road"
    direction: str = "in"      # "in" or "out"
    dow: int = 5               # Sun=0 ... Sat=6
    rain: int = 0              # 0 or 1

@app.post("/best-time")
def best_time(t: Trip):
    X = pd.DataFrame({"corridor": t.corridor, "direction": t.direction, "hour": range(5, 23), "dow": t.dow, "rain": t.rain})
    X["pred"] = model.predict(X)
    b, w = X.loc[X.pred.idxmin()], X.loc[X.pred.idxmax()]
    return {"best_hour": int(b.hour), "best_minutes": round(float(b.pred), 1),
            "worst_hour": int(w.hour), "worst_minutes": round(float(w.pred), 1),
            "hourly": {int(r.hour): round(float(r.pred), 1) for _, r in X.iterrows()}}
