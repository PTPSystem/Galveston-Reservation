#!/usr/bin/env bash
set -euo pipefail

# update.sh <ssh-host-alias> [branch]

HOST=${1:-}
BRANCH=${2:-main}
if [[ -z "$HOST" ]]; then
  echo "Usage: $0 <ssh-host-alias> [branch]" >&2
  exit 1
fi

ssh "$HOST" bash -s <<REMOTE
set -euo pipefail
cd /opt/galveston-reservation
git fetch --all --prune
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"
source .venv/bin/activate
pip install -r requirements.txt --quiet
python -c "from app import create_app, db; a=create_app(); a.app_context().push(); db.create_all()"
sudo systemctl restart galveston-reservation
sleep 2
sudo systemctl is-active --quiet galveston-reservation && echo "Service running" || (echo "Service failed"; exit 1)
REMOTE

ssh "$HOST" 'journalctl -u galveston-reservation -n 30 --no-pager'

echo "Update complete."
