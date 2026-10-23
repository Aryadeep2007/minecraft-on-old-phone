#!/data/data/com.termux/files/usr/bin/sh
set -eu

APP_DIR="${DASHBOARD_DIR:-$HOME/minecraft-on-old-phone}"
cd "$APP_DIR"

if [ ! -f .env ]; then
  echo "Missing $APP_DIR/.env; copy dashboard/.env.example to .env and configure secrets." >&2
  exit 1
fi

set -a
. ./.env
set +a

exec .venv/bin/waitress-serve --listen=127.0.0.1:8765 dashboard.app:app
