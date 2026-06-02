"""
Retraining entrypoint.

Optionally regenerates data, then retrains all models. Intended to be wired to
a scheduler (cron / Snowflake Task / Airflow) for periodic refresh.

Run:
    python -m backend.ml.retrain --regenerate
"""
from __future__ import annotations

import argparse

from . import train_all


def main(regenerate: bool = False) -> None:
    if regenerate:
        from data.data_generator import generate

        print("[retrain] regenerating dataset ...")
        generate(write=True)
    print("[retrain] retraining all models ...")
    train_all.main()
    print("[retrain] complete")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--regenerate", action="store_true", help="Regenerate synthetic data first")
    main(**vars(ap.parse_args()))
