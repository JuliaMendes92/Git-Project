#!/usr/bin/env bash
set -e

# Install Python dependencies (use pip) and start the FastAPI app
if [ -f backend/requirements.txt ]; then
  echo "Installing backend requirements..."
  python -m pip install --upgrade pip
  pip install -r backend/requirements.txt
fi

echo "Starting uvicorn..."
uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
