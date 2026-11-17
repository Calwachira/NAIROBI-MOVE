# NairobiMove: Smart Commute Explorer

Data-science project that predicts trip times on Nairobi corridors by hour, day and weather,
and recommends the best time to leave.

## Contents
- `app/index.html`: interactive dashboard. Double-click to open in a browser (no install).
- `data/generate_synthetic.py`: makes SYNTHETIC trip data. `data/trips.csv` is included.
- `src/train.py`: trains Ridge baseline and gradient boosting; prints MAE and R2 on the last 6 weeks.
- `src/best_time.py`: command-line best-time finder.
- `src/api.py`: FastAPI service (`POST /best-time`).
- `models/trip_model.joblib`: trained model (included).
- `docs/PROJECT_PLAN.md`: 10-week plan and data ideas.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/train.py                # optional: retrain
python src/best_time.py "Thika Road" in 5 --rain
uvicorn src.api:app --reload       # docs at http://127.0.0.1:8000/docs
```

## Important
The data is simulated, so scores only prove the pipeline works. For a real project, replace
`data/trips.csv` with real trips (same columns: date, corridor, direction, hour, dow, rain, trip_min) and retrain.
