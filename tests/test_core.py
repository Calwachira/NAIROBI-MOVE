import datetime as dt, re
import pytest
from fastapi.testclient import TestClient
from src import model, planner
from src.api import app
from src.calendar_ke import day_context, is_holiday, school_open
from src.config import CORRIDORS, ROOT

@pytest.fixture(scope="module")
def c():
    with TestClient(app) as client: yield client

def test_paths_are_absolute(): assert ROOT.is_absolute() and (ROOT / "src").exists()

def test_calendar():
    assert is_holiday(dt.date(2025, 4, 18)) and not is_holiday(dt.date(2025, 4, 17))
    assert school_open(dt.date(2025, 2, 10)) and not school_open(dt.date(2025, 12, 10)) and not school_open(dt.date(2025, 2, 9))
    assert day_context(date=dt.date(2025, 1, 6))["dow"] == 1            # Monday
    with pytest.raises(ValueError): day_context(dow=9)

def test_model_quality():
    m = model.bundle()["metrics"]
    assert m["r2_p50"] > .8 and m["mae_p50"] < m["mae_historical_average"] < m["mae_ridge"]
    assert .85 <= m["p90_coverage"] <= .95                              # p90 really covers about 90% of trips

def test_p90_never_below_p50_and_rush_hour_slower():
    t = model.predict_day("Thika Road", "in", day_context(dow=2))
    assert (t.p90 >= t.p50).all() and t.p50[8] > t.p50[13] > t.p50[22] * .95
    assert model.predict_day("Thika Road", "in", day_context(dow=2, rain=1)).p50[8] > t.p50[8]
    assert model.predict_day("Thika Road", "in", day_context(dow=2, holiday=True)).p50[8] < t.p50[8]

def test_best_time_is_a_commuting_hour():
    b = planner.best_time(model.predict_day("Mombasa Road", "in", day_context(dow=3)))
    assert 6 <= b["best_hour"] <= 20 and b["save_minutes"] > 5

def test_leave_by_buffer_and_impossible_deadline():
    t = model.predict_day("Thika Road", "in", day_context(dow=2)); r = planner.leave_by(t, 8 * 60 + 30)
    assert r["recommended"]["leave_at"] <= r["typical_day"]["leave_at"] and r["buffer_minutes"] >= 0
    assert planner.leave_by(t, 5 * 60 + 20)["recommended"] is None

def test_erp_prices_peaks_only():
    t = model.predict_day("Thika Road", "in", day_context(dow=2)); e = planner.erp(t, model.bundle()["free"]["Thika Road"])
    h = {r["hour"]: r for r in e["hours"]}
    assert h[8]["price_kes"] > 0 and h[13]["price_kes"] == 0 and h[22]["price_kes"] == 0
    assert all(r["minutes_after"] <= r["minutes_now"] + .01 for r in e["hours"])

def test_check_reading_flags_incident():
    t = model.predict_day("Thika Road", "in", day_context(dow=2))
    assert planner.check_reading(t, 8, float(t.p50[8]))["status"] == "normal"
    assert planner.check_reading(t, 8, float(t.p90[8]) * 1.5)["status"] == "possible_incident"

@pytest.mark.parametrize("body", [{"corridor": "Nowhere Rd"}, {"direction": "sideways"}, {"dow": 42}, {"rain": 9}])
def test_api_rejects_bad_input(c, body):
    assert c.post("/best-time", json=body).status_code == 422             # the old API returned 200 with garbage

def test_api_endpoints(c):
    assert c.get("/health").json()["status"] == "ok" and len(c.get("/corridors").json()["corridors"]) == 6
    b = c.post("/best-time", json={"date": "2026-12-11"}).json(); assert b["hourly_p90"] and b["best_minutes"] < b["worst_minutes"]
    assert c.post("/leave-by", json={"arrive_by": "08:30", "dow": 2}).json()["recommended"]["leave_at"]
    assert c.post("/leave-by", json={"arrive_by": "25:00"}).status_code == 422
    assert c.post("/erp", json={"dow": 2, "target": 1.3}).json()["peak_price_kes"] > 0
    assert c.post("/check-reading", json={"hour": 8, "observed_min": 200, "dow": 2}).json()["status"] == "possible_incident"
    assert c.get("/").status_code == 200                                  # dashboard is served too

def test_dashboard_copy_of_corridors_matches_python():
    html = (ROOT / "app" / "index.html").read_text()
    found = {n: (float(f), float(a), float(m)) for n, f, a, m in re.findall(r'\{n:"([^"]+)",f:([\d.]+),a:([\d.]+),m:([\d.]+)\}', html)}
    assert found == {k: tuple(map(float, v)) for k, v in CORRIDORS.items()}
