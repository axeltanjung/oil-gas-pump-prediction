# Models

Trained artifacts are written here by the training scripts (git-ignored):
- `failure_xgb.joblib` — Model 1 (XGBoost classifier)
- `rul_xgb.joblib` — Model 2 (XGBoost regressor)
- `forecast_lstm.pt` — Model 3 (PyTorch LSTM)
- `feature_meta.json` — engineered feature column order
- `failure_shap.json`, `*_feature_importance.json` — explainability artifacts

Generate them with: `python -m backend.ml.train_all`
