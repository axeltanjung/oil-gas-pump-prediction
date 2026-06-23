#!/usr/bin/env bash
# Post-create setup for GitHub Codespaces
# Co-authored with CoCo
set -euo pipefail

echo "=== Setting up Python environment ==="
python -m venv /workspace/.venv
source /workspace/.venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install ruff pytest pytest-cov

echo "=== Setting up frontend ==="
cd frontend && npm install && cd ..

echo "=== Copying env file ==="
if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "=== Done! ==="
echo "Backend:  uvicorn app.main:app --reload (port 8000)"
echo "Frontend: cd frontend && npm run dev     (port 5173)"
