#!/usr/bin/env sh
# ──────────────────────────────────────────────
# run_prod.sh — Production startup script
# Usage: sh run_prod.sh
# Requires: .env file to exist in this directory
# ──────────────────────────────────────────────

set -e

# Ensure .env exists
if [ ! -f ".env" ]; then
  echo "ERROR: .env file not found."
  echo "Copy .env.example to .env and fill in your secret values:"
  echo "  cp .env.example .env"
  exit 1
fi

# Activate venv if present
if [ -d "venv" ]; then
  . venv/bin/activate
fi

echo "Starting MediCore in PRODUCTION mode..."
APP_ENV=production python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --proxy-headers \
  --forwarded-allow-ips='*'
