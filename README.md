# NairobiMove v2: Smart Commute Explorer

Predicts trip times on six Nairobi corridors by hour, day, weather, school terms and public holidays,
then turns the predictions into decisions: when to leave, when to be on the road to arrive on time,
what road pricing would do, and whether today's trip is abnormally slow.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.api:app --reload         # dashboard: http://127.0.0.1:8000   API docs: http://127.0.0.1:8000/docs
```
The first start trains the model (about 20 seconds). Use `http://127.0.0.1:8000`, not `0.0.0.0`, in the browser.
No install is needed for the dashboard alone: double-click `app/index.html`.

Other commands (all work from any folder):
```bash
python src/train.py                                              # retrain + accuracy report
python src/best_time.py "Thika Road" in 5 --rain                 # day number: Sun=0 ... Sat=6
python src/best_time.py "Thika Road" in 2026-12-11 --arrive-by 08:30 --erp
python data/generate_synthetic.py                                # rebuild the simulated data
pip install -r requirements-dev.txt && pytest                    # 14 tests
```

## Singapore-style features
| Idea from Singapore | In NairobiMove |
|---|---|
| Reliability, not just averages (planning time, buffer time) | `p90` model: how long the trip takes on a bad day. Reported as a buffer index. |
| "Arrive by" journey planning | `/leave-by`: latest departure that arrives on time 9 days in 10, and how many minutes of buffer that costs. |
| Electronic Road Pricing (rates set to hold speeds) | `/erp`: price per departure hour that keeps trips under a target multiple of free-flow time. |
| Incident detection (EMAS) | `/check-reading`: compares a live trip time with what is expected: normal, slower than usual, possible incident. |
| Calendar-aware planning | Public holidays and school terms are model features; pass a `date` and they are worked out for you. |

## API
```bash
curl -X POST localhost:8000/best-time   -H "Content-Type: application/json" -d '{"corridor":"Thika Road","date":"2026-12-11","rain":1}'
curl -X POST localhost:8000/leave-by    -H "Content-Type: application/json" -d '{"corridor":"Thika Road","dow":2,"arrive_by":"08:30"}'
curl -X POST localhost:8000/erp         -H "Content-Type: application/json" -d '{"corridor":"Mombasa Road","dow":2,"target":1.4}'
curl -X POST localhost:8000/check-reading -H "Content-Type: application/json" -d '{"corridor":"Thika Road","dow":2,"hour":8,"observed_min":120}'
```
Also `GET /health` (model metrics) and `GET /corridors`. Invalid input returns HTTP 422 with a clear message.

## Accuracy (on SIMULATED data, last 8 weeks held out)
| Method | Average error |
|---|---|
| Historical average lookup | 6.3 min |
| Ridge baseline | 7.9 min |
| Gradient boosting (typical trip) | 3.1 min, R2 0.87 |
| p90 model | covers 89% of trips (target 90%) |

The data is simulated, so these numbers show the pipeline works, not how Nairobi really behaves.

## Folders
```
app/index.html          dashboard (works alone, or served by the API)
data/                   trips.csv (simulated) and its generator
src/config.py           corridors, paths     src/calendar_ke.py   holidays and school terms
src/synth.py            data simulator       src/model.py         training, loading, prediction
src/planner.py          best time, arrive-by, road pricing, incident check
src/api.py, train.py, best_time.py           API and command-line tools
tests/                  14 tests             docs/                plan and change log
```

## Before using it for real
1. Replace `data/trips.csv` with real trips (columns: date, corridor, direction, hour, dow, rain, holiday, school, trip_min) and retrain.
2. Check `src/calendar_ke.py`: holidays and term dates are approximate. Islamic holidays are not listed.
3. The road-pricing demand response (25% fewer cars per KES 100) is an assumption. Measure it before trusting any price.
4. Keep data at corridor-hour level; do not store personal location trails.
