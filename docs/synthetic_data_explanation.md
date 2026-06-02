# Synthetic Dataset Explanation

The dataset (`data/pump_telemetry.csv`, mirrored in SQLite `data/pumps.db` table `telemetry`)
is produced by `data/data_generator.py`. It simulates hourly sensor telemetry for a fleet of
industrial Oil & Gas pumps over time.

## Scale
- **Pumps:** `N_PUMPS` (default 25)
- **Hours per pump:** `N_HOURS` (default 4,500)
- **Total rows:** ~112,500 (≥ 100,000 requirement)
- **Frequency:** hourly timestamps starting `2024-01-01`

## Columns

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime | Hourly reading time |
| `pump_id` | string | Pump identifier (`PUMP-001` …) |
| `pressure` | float (bar) | Discharge pressure; drops with wear, dips on cavitation |
| `vibration` | float (mm/s) | Rises with degradation; random spikes |
| `temperature` | float (°C) | Rises with degradation; overheating events |
| `rpm` | float | Shaft speed; mildly unstable near failure |
| `flow_rate` | float (m³/h) | Decreases with wear and cavitation |
| `operating_hours` | float | Cumulative running hours (asset age) |
| `maintenance_history` | int | Count of maintenance/replacement events so far |
| `ambient_temperature` | float (°C) | Environmental temperature (seasonal sine + noise) |
| `power_consumption` | float (kW) | Increases as the pump strains |
| `health_index` | float 0–1 | Latent health state (ground truth, useful for the LSTM target) |
| `failure_event` | int 0/1 | 1 at the exact hour a failure occurs |
| **`failure_within_7_days`** | int 0/1 | **Target (Model 1):** failure occurs within the next 7 days |
| **`rul_days`** | float | **Target (Model 2):** Remaining Useful Life in days |
| **`anomaly_score`** | float 0–1 | **Target (Model 3 / anomaly):** composite risk score |

## Simulated physics & failure modes
- **Normal degradation:** `health_index` decays nonlinearly with operating hours (decay accelerates as the pump ages within a cycle: `wear_rate * (1 + 3.5·frac²)`).
- **Gradual wear:** sensors drift proportional to degradation `deg = 1 − health`.
- **Sudden failure:** ~35% of cycles get a steep terminal decay multiplier in the final 15% of life.
- **Sensor noise:** Gaussian noise added to every channel.
- **Overheating:** rare temperature jumps (+8–18 °C).
- **Cavitation:** correlated pressure drops and flow dips.
- **Vibration spikes:** rare transient spikes (+2–6 mm/s).
- **Maintenance/repair:** at failure, health resets to ~0.95–1.0 and `maintenance_history` increments (creates multiple degradation cycles per pump).

## Target derivation
- `rul_days` = hours until the *next* `failure_event`, converted to days.
- `failure_within_7_days` = 1 when RUL ≤ 7 days (`FAILURE_HORIZON_DAYS`).
- `anomaly_score` = normalized blend of degradation + positive vibration/temperature z-scores.

## Reproducibility
Controlled by `RANDOM_SEED` (default 42). Adjust `N_PUMPS`, `N_HOURS`,
`FAILURE_HORIZON_DAYS` via environment variables / `.env`.
