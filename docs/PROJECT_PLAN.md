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

## Roadmap toward Singapore-level operation
| Step | What | Why |
|------|------|-----|
| 1 | Replace simulated data with real probe data (GPS volunteers, matatu or BRT fleets, Distance Matrix samples) | Everything else depends on real measurements |
| 2 | Split corridors into road segments with speed bands | Singapore manages speed on each stretch, not whole roads |
| 3 | Measure real price and timing response (pilot incentives for off-peak travel) | Replaces the assumed elasticity in the road-pricing tool |
| 4 | Feed live readings into `/check-reading` every 5 minutes | Incident detection in minutes, not hours |
| 5 | Add bus-priority and signal-timing scenarios | Moves more people, not only more cars |
| 6 | Track measured minutes saved per commuter | The honest success measure |
