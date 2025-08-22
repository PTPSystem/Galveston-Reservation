#!/usr/bin/env bash
set -euo pipefail

# deploy/scripts/deploy.sh <ssh-host-alias> [branch]
# Idempotent initial (or repeat) deployment.

HOST=${1:-}
BRANCH=${2:-main}
APP_DIR=/opt/galveston-reservation
SERVICE=galveston-reservation.service

if [[ -z "$HOST" ]]; then
  echo "Usage: $0 <ssh-host-alias> [branch]" >&2
  exit 1
fi

echo "==> Connecting to $HOST (branch: $BRANCH)"

ssh "$HOST" bash -s <<'REMOTE'
set -euo pipefail
APP_DIR=/opt/galveston-reservation
REPO_URL="https://github.com/PTPSystem/Galveston-Reservation.git"

echo "[Remote] Creating app directory..."
sudo mkdir -p "${APP_DIR}" || true
sudo chown "$(whoami):$(whoami)" "$APP_DIR"

if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "[Remote] Cloning repository..."
  git clone "$REPO_URL" "$APP_DIR"
else
  echo "[Remote] Repository exists, fetching..."
  git -C "$APP_DIR" fetch --all --prune
fi
REMOTE

echo "==> Checking out branch on remote"
ssh "$HOST" bash -s <<REMOTE
set -euo pipefail
APP_DIR=/opt/galveston-reservation
cd "$APP_DIR"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "[Remote] Creating venv (if missing)..."
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[Remote] Creating directories..."
mkdir -p logs secrets

if [[ ! -f .env ]]; then
  echo "[Remote] Creating placeholder .env (edit with real secrets)."
  cp .env.example .env || true
fi

echo "[Remote] Initializing database (sqlite if configured)..."
python -c "from app import create_app, db; a=create_app(); a.app_context().push(); db.create_all(); print('DB ok')"
REMOTE

echo "==> Installing / updating systemd unit"
scp deploy/systemd/galveston-reservation.service "$HOST":/tmp/galveston-reservation.service
ssh "$HOST" 'sudo mv /tmp/galveston-reservation.service /etc/systemd/system/galveston-reservation.service && sudo systemctl daemon-reload'

echo "==> (Re)starting service"
ssh "$HOST" 'sudo systemctl enable galveston-reservation --now'
ssh "$HOST" 'sudo systemctl status --no-pager --lines=5 galveston-reservation || true'

echo "==> Tail last 20 log lines"
ssh "$HOST" 'journalctl -u galveston-reservation -n 20 --no-pager'

echo "Deployment complete. Edit /opt/galveston-reservation/.env with production values if not done."
