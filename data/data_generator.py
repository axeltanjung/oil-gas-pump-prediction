"""
Synthetic Oil & Gas pump telemetry generator.

Produces a realistic, time-series, multi-pump dataset that simulates:
  - normal degradation (slow health decay over operating hours)
  - sensor noise
  - overheating events
  - cavitation (pressure/flow instability)
  - vibration spikes
  - gradual wear
  - sudden failure patterns

Outputs:
  - data/pump_telemetry.csv
  - data/pumps.db  (SQLite, table `telemetry`)

Run:
    python -m data.data_generator
"""
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Configuration (overridable via environment / .env)
# ----------------------------------------------------------------------------
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__)))
CSV_PATH = os.path.join(DATA_DIR, "pump_telemetry.csv")
SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(DATA_DIR, "pumps.db"))

N_PUMPS = int(os.getenv("N_PUMPS", "25"))
N_HOURS = int(os.getenv("N_HOURS", "4500"))  # 25 * 4500 = 112,500 rows >= 100k
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
FAILURE_HORIZON_DAYS = int(os.getenv("FAILURE_HORIZON_DAYS", "7"))

START_TIME = datetime(2024, 1, 1, 0, 0, 0)

rng = np.random.default_rng(RANDOM_SEED)


# ----------------------------------------------------------------------------
# Per-pump baseline characteristics (each pump is slightly different)
# ----------------------------------------------------------------------------
@dataclass
class PumpProfile:
    pump_id: str
    base_pressure: float        # bar
    base_vibration: float       # mm/s
    base_temperature: float     # deg C
    base_rpm: float
    base_flow: float            # m3/h
    base_power: float           # kW
    wear_rate: float            # health decay per hour
    install_hours: float        # operating hours at t0


def _make_profiles() -> list[PumpProfile]:
    profiles = []
    for i in range(N_PUMPS):
        profiles.append(
            PumpProfile(
                pump_id=f"PUMP-{i + 1:03d}",
                base_pressure=float(rng.uniform(45, 65)),
                base_vibration=float(rng.uniform(1.5, 3.0)),
                base_temperature=float(rng.uniform(55, 70)),
                base_rpm=float(rng.uniform(1450, 1550)),
                base_flow=float(rng.uniform(120, 200)),
                base_power=float(rng.uniform(75, 120)),
                wear_rate=float(rng.uniform(0.6, 1.6)) / N_HOURS,
                install_hours=float(rng.uniform(2000, 20000)),
            )
        )
    return profiles


# ----------------------------------------------------------------------------
# Failure-cycle simulation for a single pump
# ----------------------------------------------------------------------------
def _simulate_pump(profile: PumpProfile) -> pd.DataFrame:
    """Generate a full hourly telemetry series for one pump.

    The pump goes through one or more degradation cycles. Health decays from
    1.0 toward 0.0; at the end of each cycle a failure occurs, maintenance is
    performed, and health resets (gradual wear / repair pattern).
    """
    n = N_HOURS
    health = np.empty(n)
    failure_event = np.zeros(n, dtype=int)      # 1 at the hour a failure happens
    maintenance_history = np.zeros(n, dtype=int)  # cumulative maintenance count
    op_hours = np.empty(n)

    # Build degradation cycles of random length
    h = 1.0
    cycle_len = int(rng.uniform(700, 1600))
    cycle_pos = 0
    maint_count = int(rng.integers(0, 4))
    cumulative_op = profile.install_hours

    # randomly assign a "sudden failure" cycle (steep terminal decay)
    sudden_cycle = rng.random() < 0.35

    for t in range(n):
        # Nonlinear decay: accelerates as the pump ages within the cycle
        frac = cycle_pos / cycle_len
        decay = profile.wear_rate * (1.0 + 3.5 * frac**2)
        if sudden_cycle and frac > 0.85:
            decay *= rng.uniform(2.0, 4.0)  # sudden terminal failure
        h -= decay + rng.normal(0, 0.0004)
        h = float(np.clip(h, 0.0, 1.0))

        health[t] = h
        op_hours[t] = cumulative_op
        maintenance_history[t] = maint_count
        cumulative_op += 1.0
        cycle_pos += 1

        # Failure when health bottoms out (or cycle exhausted)
        if h <= rng.uniform(0.02, 0.06) or cycle_pos >= cycle_len:
            failure_event[t] = 1
            # maintenance / replacement -> reset
            h = float(rng.uniform(0.95, 1.0))
            cycle_len = int(rng.uniform(700, 1600))
            cycle_pos = 0
            maint_count += 1
            sudden_cycle = rng.random() < 0.35

    # ----- Derive sensor signals from health -----
    deg = 1.0 - health  # degradation 0..1

    # Vibration rises sharply with degradation + random spikes
    vibration = (
        profile.base_vibration
        + deg * rng.uniform(6, 10)
        + rng.normal(0, 0.15, n)
    )
    spike_idx = rng.random(n) < 0.01
    vibration[spike_idx] += rng.uniform(2, 6, spike_idx.sum())

    # Temperature rises with degradation; overheating events
    ambient = 25 + 8 * np.sin(np.linspace(0, 8 * np.pi, n)) + rng.normal(0, 1.0, n)
    temperature = (
        profile.base_temperature
        + deg * rng.uniform(20, 35)
        + 0.3 * (ambient - 25)
        + rng.normal(0, 0.8, n)
    )
    overheat_idx = rng.random(n) < 0.008
    temperature[overheat_idx] += rng.uniform(8, 18, overheat_idx.sum())

    # Pressure drops as the pump wears; cavitation = unstable pressure/flow
    pressure = (
        profile.base_pressure
        - deg * rng.uniform(10, 20)
        + rng.normal(0, 0.6, n)
    )
    cavitation_idx = rng.random(n) < 0.012
    pressure[cavitation_idx] -= rng.uniform(5, 12, cavitation_idx.sum())

    # RPM slightly unstable near failure
    rpm = profile.base_rpm - deg * rng.uniform(20, 60) + rng.normal(0, 5, n)

    # Flow rate decreases with wear and cavitation
    flow_rate = (
        profile.base_flow
        - deg * rng.uniform(25, 50)
        + rng.normal(0, 2.0, n)
    )
    flow_rate[cavitation_idx] -= rng.uniform(10, 25, cavitation_idx.sum())

    # Power consumption increases as the pump strains
    power = (
        profile.base_power
        + deg * rng.uniform(15, 30)
        + rng.normal(0, 1.5, n)
    )

    # ----- Targets -----
    # RUL: hours until next failure -> days
    rul_hours = np.empty(n)
    next_fail = n  # if no future failure, treat as far away
    for t in range(n - 1, -1, -1):
        if failure_event[t] == 1:
            next_fail = t
        rul_hours[t] = max(next_fail - t, 0)
    rul_days = np.round(rul_hours / 24.0, 2)

    horizon_hours = FAILURE_HORIZON_DAYS * 24
    failure_within_7_days = (rul_hours <= horizon_hours).astype(int)

    # Anomaly score 0..1: combination of degradation + transient events
    z_vib = (vibration - profile.base_vibration) / (vibration.std() + 1e-6)
    z_temp = (temperature - profile.base_temperature) / (temperature.std() + 1e-6)
    anomaly_raw = 0.5 * deg + 0.25 * np.clip(z_vib, 0, None) + 0.25 * np.clip(z_temp, 0, None)
    anomaly_score = np.round(np.clip(anomaly_raw / (anomaly_raw.max() + 1e-6), 0, 1), 4)

    timestamps = [START_TIME + timedelta(hours=int(t)) for t in range(n)]

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "pump_id": profile.pump_id,
            "pressure": np.round(pressure, 3),
            "vibration": np.round(vibration, 3),
            "temperature": np.round(temperature, 3),
            "rpm": np.round(rpm, 2),
            "flow_rate": np.round(flow_rate, 3),
            "operating_hours": np.round(op_hours, 1),
            "maintenance_history": maintenance_history,
            "ambient_temperature": np.round(ambient, 2),
            "power_consumption": np.round(power, 3),
            "health_index": np.round(health, 4),
            "failure_event": failure_event,
            "failure_within_7_days": failure_within_7_days,
            "rul_days": rul_days,
            "anomaly_score": anomaly_score,
        }
    )


# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------
def generate(write: bool = True) -> pd.DataFrame:
    """Generate the full multi-pump dataset and (optionally) persist it."""
    profiles = _make_profiles()
    frames = [_simulate_pump(p) for p in profiles]
    df = pd.concat(frames, ignore_index=True)
    df.sort_values(["pump_id", "timestamp"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    if write:
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(CSV_PATH, index=False)
        _write_sqlite(df)
        print(f"[data_generator] Wrote {len(df):,} rows -> {CSV_PATH}")
        print(f"[data_generator] SQLite -> {SQLITE_PATH} (table: telemetry)")
        _print_summary(df)
    return df


def _write_sqlite(df: pd.DataFrame) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(SQLITE_PATH)), exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    try:
        out = df.copy()
        out["timestamp"] = out["timestamp"].astype(str)
        out.to_sql("telemetry", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pump ON telemetry(pump_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON telemetry(timestamp)")
        conn.commit()
    finally:
        conn.close()


def _print_summary(df: pd.DataFrame) -> None:
    print("\n[data_generator] Summary")
    print(f"  pumps:                {df['pump_id'].nunique()}")
    print(f"  rows:                 {len(df):,}")
    print(f"  failures (events):    {int(df['failure_event'].sum()):,}")
    print(f"  positive 7d label %:  {100 * df['failure_within_7_days'].mean():.2f}%")
    print(f"  rul_days range:       [{df['rul_days'].min()}, {df['rul_days'].max()}]")
    print(f"  anomaly_score mean:   {df['anomaly_score'].mean():.3f}")


if __name__ == "__main__":
    generate(write=True)
