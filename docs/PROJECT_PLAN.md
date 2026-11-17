# NairobiMove: 10-week plan

| Weeks | Focus | Deliverable |
|-------|-------|-------------|
| 1-2 | Frame and collect | Pick corridors, define trip-time target, first data pulls (Uber Movement, Distance Matrix samples, own GPS logs) |
| 3-4 | Clean and explore | Hour x day heatmaps, rain effect, outlier handling, data-quality report |
| 5-6 | Model | Baseline (Ridge) vs gradient boosting, time-based validation, MAE by hour |
| 7-8 | Extend | Add features: school terms, public holidays, matatu strike days, events, rainfall data |
| 9-10 | Ship and present | API, dashboard linked to API, final report with measured minutes saved |

## Data ideas (verify access and licences)
Uber Movement (where available), Google Maps Distance Matrix sampling, OpenStreetMap road network,
CHIRPS/ERA5 rainfall, Kenya public-holiday calendar, student GPS volunteers.

## Ethics
Do not store raw personal location trails. Aggregate to corridor-hour. Be clear that predictions are estimates.
