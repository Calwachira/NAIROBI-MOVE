"""Run:  uvicorn src.api:app --reload   (from the project folder)   then open http://127.0.0.1:8000  (dashboard)  or /docs  (API)"""
import datetime as dt
from contextlib import asynccontextmanager
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from src import model, planner
from src.calendar_ke import day_context
from src.config import CORRIDORS, ROOT

@asynccontextmanager
async def lifespan(app):
    model.bundle(); yield            # load (or train) once at start-up, not on the first request

app = FastAPI(title="NairobiMove API", version="2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Trip(BaseModel):
    corridor: str = "Thika Road"
    direction: Literal["in", "out"] = "in"
    date: Optional[dt.date] = Field(None, description="If given, day of week, public holiday and school term are worked out for you")
    dow: Optional[int] = Field(None, ge=0, le=6, description="Sun=0 ... Sat=6 (used when date is empty)")
    rain: Literal[0, 1] = 0
    holiday: Optional[bool] = None
    school: Optional[bool] = None
    @field_validator("corridor")
    @classmethod
    def known(cls, v):
        if v not in CORRIDORS: raise ValueError(f"Unknown corridor. Choose from: {', '.join(CORRIDORS)}")
        return v
    def table(self):
        return model.predict_day(self.corridor, self.direction, day_context(self.date, self.dow, self.rain, self.holiday, self.school))

class LeaveBy(Trip): arrive_by: str = Field("08:30", pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
class Erp(Trip):
    target: float = Field(1.45, ge=1.1, le=3, description="Keep trips under this multiple of free-flow time")
    elasticity: float = Field(-.25, ge=-1, le=-.05, description="Share of demand lost per KES 100")
class Reading(Trip):
    hour: int = Field(8, ge=5, le=22)
    observed_min: float = Field(gt=0, le=600)

@app.get("/health")
def health():
    b = model.bundle(); return {"status": "ok", "sklearn": b["sklearn"], "metrics": b["metrics"]}
@app.get("/corridors")
def corridors(): return {"corridors": list(CORRIDORS), "free_flow_minutes": {k: round(v) for k, v in model.bundle()["free"].items()}}
@app.post("/best-time")
def best_time(t: Trip): return planner.best_time(t.table())
@app.post("/leave-by")
def leave_by(q: LeaveBy): h, m = map(int, q.arrive_by.split(":")); return planner.leave_by(q.table(), h * 60 + m)
@app.post("/erp")
def erp(q: Erp): return planner.erp(q.table(), model.bundle()["free"][q.corridor], q.target, q.elasticity)
@app.post("/check-reading")
def check(q: Reading): return planner.check_reading(q.table(), q.hour, q.observed_min)

app.mount("/", StaticFiles(directory=ROOT / "app", html=True), name="dashboard")   # keep last
