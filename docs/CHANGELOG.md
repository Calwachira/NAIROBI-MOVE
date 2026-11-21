# What changed in v2

## Bugs fixed
| # | Problem in v1 | Fix |
|---|---|---|
| 1 | Scripts only worked when run from the project folder (`data/trips.csv` not found otherwise) | Absolute paths in `src/config.py`; every script works from any folder |
| 2 | API and CLI accepted nonsense and answered with confidence (`"Thika Rd"`, `dow=42`, `direction="sideways"`, `rain=9` all returned 200) | Input validation: HTTP 422 with a clear message; CLI prints a readable error |
| 3 | "Best time to leave" was usually 10pm | Best/worst now chosen inside a 6am to 8pm commuting window |
| 4 | Saved model file breaks or misbehaves on a different scikit-learn version | Model records its version; it is rebuilt automatically when missing or mismatched, and is no longer shipped |
| 5 | Model loaded at import and predictions recomputed on every request | Loaded once at start-up; predictions cached |
| 6 | Dashboard re-implemented the model by hand, so it could silently drift from the Python code | A test now fails if the dashboard's corridor numbers differ from `src/config.py` |
| 7 | Data had no holidays, school terms or incidents; errors were pure noise | 52 weeks, Kenyan calendar features, rare incidents (heavy tails) |
| 8 | Baselines were unfair or missing (day number fed to a linear model; no simple lookup) | Added the historical-average benchmark every real system must beat |
| 9 | No tests, no CORS, dashboard not served by the API | 14 tests, CORS, dashboard served at `/` |

## Added
p90 reliability model and buffer index, arrive-by planner, road-pricing recommender, incident check,
calendar features, `--date` support, dashboard panels for all of the above, school and holiday toggles.

## Known limits
Simulated data. Approximate calendar. Road-pricing elasticity is assumed. One simulated rain flag per day for all corridors.
