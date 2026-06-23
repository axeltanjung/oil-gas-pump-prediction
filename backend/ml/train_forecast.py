"""
Model 3 - Time-Series Degradation Forecast (PyTorch LSTM).

Learns to predict the next-step health index from a sliding window of recent
sensor readings, enabling health-trend / degradation forecasting.

Run:
    python -m backend.ml.train_forecast
"""

from __future__ import annotations

import json
import os

import joblib
import numpy as np
import pandas as pd

from . import config, mlflow_utils, preprocessing

SEQ_FEATURES = [
    "pressure",
    "vibration",
    "temperature",
    "rpm",
    "flow_rate",
    "power_consumption",
]


# ----------------------------------------------------------------------------
# Sequence windowing
# ----------------------------------------------------------------------------
def build_sequences(df: pd.DataFrame, seq_len: int):
    """Create (X, y) sliding windows per pump. y = next-step health_index."""
    X_list, y_list = [], []
    for _, grp in df.sort_values(["pump_id", "timestamp"]).groupby("pump_id"):
        feats = grp[SEQ_FEATURES].to_numpy(dtype=np.float32)
        target = grp[config.TARGET_HEALTH].to_numpy(dtype=np.float32)
        for i in range(len(grp) - seq_len):
            X_list.append(feats[i : i + seq_len])
            y_list.append(target[i + seq_len])
    if not X_list:
        return np.empty((0, seq_len, len(SEQ_FEATURES))), np.empty((0,))
    return np.stack(X_list), np.array(y_list, dtype=np.float32)


def train() -> dict:
    config.ensure_dirs()
    try:
        import torch
        from torch import nn
        from torch.utils.data import DataLoader, TensorDataset
    except Exception as exc:  # pragma: no cover
        print(f"[train_forecast] PyTorch unavailable, skipping LSTM: {exc}")
        return {}

    torch.manual_seed(config.RANDOM_SEED)
    np.random.seed(config.RANDOM_SEED)

    df = preprocessing.basic_clean(preprocessing.load_dataset())

    # Scale features (fit on full set; persisted for inference).
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    df[SEQ_FEATURES] = scaler.fit_transform(df[SEQ_FEATURES])

    seq_len = config.LSTM_SEQUENCE_LEN
    X, y = build_sequences(df, seq_len)
    if len(X) == 0:
        print("[train_forecast] not enough data for sequences")
        return {}

    cut = int(len(X) * 0.8)
    X_tr, X_te = X[:cut], X[cut:]
    y_tr, y_te = y[:cut], y[cut:]

    device = "cuda" if torch.cuda.is_available() else "cpu"

    class LSTMForecaster(nn.Module):
        def __init__(self, n_features, hidden, layers):
            super().__init__()
            self.lstm = nn.LSTM(
                n_features,
                hidden,
                layers,
                batch_first=True,
                dropout=0.2 if layers > 1 else 0.0,
            )
            self.head = nn.Sequential(
                nn.Linear(hidden, 32), nn.ReLU(), nn.Linear(32, 1), nn.Sigmoid()
            )

        def forward(self, x):
            out, _ = self.lstm(x)
            return self.head(out[:, -1, :]).squeeze(-1)

    model = LSTMForecaster(
        len(SEQ_FEATURES), config.LSTM_HIDDEN, config.LSTM_LAYERS
    ).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=config.LSTM_LR)
    loss_fn = nn.MSELoss()

    train_ds = TensorDataset(torch.from_numpy(X_tr), torch.from_numpy(y_tr))
    loader = DataLoader(train_ds, batch_size=config.LSTM_BATCH, shuffle=True)

    params = dict(
        seq_len=seq_len,
        hidden=config.LSTM_HIDDEN,
        layers=config.LSTM_LAYERS,
        lr=config.LSTM_LR,
        epochs=config.LSTM_EPOCHS,
        batch=config.LSTM_BATCH,
        n_features=len(SEQ_FEATURES),
    )

    with mlflow_utils.start_run("forecast_lstm"):
        mlflow_utils.log_params(params)
        model.train()
        for epoch in range(config.LSTM_EPOCHS):
            running = 0.0
            for xb, yb in loader:
                xb, yb = xb.to(device), yb.to(device)
                opt.zero_grad()
                out = model(xb)
                loss = loss_fn(out, yb)
                loss.backward()
                opt.step()
                running += loss.item() * len(xb)
            epoch_loss = running / len(train_ds)
            mlflow_utils.log_metrics({"train_mse": epoch_loss})
            print(
                f"[train_forecast] epoch {epoch + 1}/{config.LSTM_EPOCHS} mse={epoch_loss:.5f}"
            )

        # Evaluation
        model.eval()
        with torch.no_grad():
            pred = model(torch.from_numpy(X_te).to(device)).cpu().numpy()
        rmse = float(np.sqrt(np.mean((pred - y_te) ** 2)))
        mae = float(np.mean(np.abs(pred - y_te)))
        metrics = {"rmse": rmse, "mae": mae}
        mlflow_utils.log_metrics(metrics)

        # Persist model + scaler + metadata
        torch.save(
            {
                "state_dict": model.state_dict(),
                "params": params,
                "seq_features": SEQ_FEATURES,
            },
            config.FORECAST_MODEL_FILE,
        )
        joblib.dump(scaler, config.SCALER_FILE)
        mlflow_utils.log_artifact(config.FORECAST_MODEL_FILE)

    out = os.path.join(config.MODEL_DIR, "forecast_metrics.json")
    with open(out, "w") as f:
        json.dump(metrics, f, indent=2)

    print(
        "[train_forecast] metrics:",
        json.dumps({k: round(v, 5) for k, v in metrics.items()}),
    )
    return metrics


if __name__ == "__main__":
    train()
