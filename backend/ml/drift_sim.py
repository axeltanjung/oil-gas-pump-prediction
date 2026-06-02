"""
Model drift simulation.

Injects synthetic drift (sensor bias + variance inflation) into a copy of the
telemetry data so you can observe degraded model performance and trigger
retraining. Writes `data/pump_telemetry_drifted.csv`.

Run:
    python -m backend.ml.drift_sim --bias 0.15 --noise 1.5
"""
from __future__ import annotations

import argparse
import os

import numpy as np

from . import config, preprocessing

DRIFT_COLS = ["pressure", "vibration", "temperature", "flow_rate", "power_consumption"]


def simulate(bias: float = 0.15, noise: float = 1.5, seed: int = 7) -> str:
    rng = np.random.default_rng(seed)
    df = preprocessing.load_dataset().copy()

    for col in DRIFT_COLS:
        col_std = df[col].std()
        df[col] = df[col] * (1 + bias) + rng.normal(0, noise * 0.1 * col_std, len(df))

    out = os.path.join(config.DATA_DIR, "pump_telemetry_drifted.csv")
    df.to_csv(out, index=False)
    print(f"[drift_sim] bias={bias} noise={noise} -> {out}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bias", type=float, default=0.15)
    ap.add_argument("--noise", type=float, default=1.5)
    simulate(**vars(ap.parse_args()))
