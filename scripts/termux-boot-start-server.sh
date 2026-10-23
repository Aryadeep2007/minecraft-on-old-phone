#!/data/data/com.termux/files/usr/bin/sh
set -eu

# Keep Termux's CPU awake while the server runs after Android boots.
termux-wake-lock

# Restore the phone's SSH access after Android boots, without duplicating it.
if ! pgrep -x sshd >/dev/null 2>&1; then
    sshd
fi

SERVER_DIR="$HOME/minecraft-server"
LOG_DIR="$SERVER_DIR/logs"

mkdir -p "$LOG_DIR"
cd "$SERVER_DIR"

# Avoid starting a second Paper process if this script is run manually.
if pgrep -f '[j]ava .* -jar paper\.jar' >/dev/null 2>&1; then
    exit 0
fi

nohup ./start.sh >> "$LOG_DIR/console.log" 2>&1 < /dev/null &
