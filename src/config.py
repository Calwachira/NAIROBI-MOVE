"""Shared settings. Paths are absolute, so every script works from any folder."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA, MODEL = ROOT / "data" / "trips.csv", ROOT / "models" / "trip_model.joblib"
# name: (free-flow minutes, congestion sensitivity, midday factor)   <- also copied into app/index.html (tests check they match)
CORRIDORS = {"Thika Road": (32, 1.3, 1.0), "Mombasa Road": (35, 1.5, .9), "Waiyaki Way": (28, 1.1, 1.0),
             "Ngong Road": (26, 1.2, 1.1), "Jogoo Road": (22, 1.0, 1.2), "Limuru Road": (24, .9, .9)}
CAT, NUM = ["corridor", "direction"], ["hour", "dow", "rain", "holiday", "school"]
HOURS = range(5, 23)       # departure hours the model covers
COMMUTE = (6, 20)          # window used for "best time to leave"
