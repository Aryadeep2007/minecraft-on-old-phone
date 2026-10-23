#!/data/data/com.termux/files/usr/bin/sh
set -eu

# Keep the public Java tunnel available after Android starts. The Playit
# credential remains inside Alpine PRoot; this script contains no secrets.
CONTAINER="alpine-musl-test"
AGENT="/root/.local/bin/playit"
SECRET_PATH="/root/.config/playit_gg/playit.toml"
SOCKET_PATH="/root/.cache/playit/playitd.sock"
LOG_DIR="$HOME/.local/var/log"
LOG_FILE="$LOG_DIR/playit-agent.log"

mkdir -p "$LOG_DIR"
chmod 700 "$LOG_DIR"

# Avoid duplicate agent instances when the boot hook is invoked more than once.
if pgrep -f '[p]layit --secret-path /root/.config/playit_gg/playit.toml' >/dev/null 2>&1; then
    exit 0
fi

# Do not start a broken agent or expose its private configuration in output.
if ! proot-distro login "$CONTAINER" -- /bin/sh -c \
    'test -x "$1" && test -f "$2"' sh "$AGENT" "$SECRET_PATH"; then
    printf '%s\n' "Playit agent or private config is missing from $CONTAINER; tunnel was not started." >&2
    exit 1
fi

# Agent logs may contain connection metadata, so keep the file private and
# never copy it into the repository or print it in a boot message.
touch "$LOG_FILE"
chmod 600 "$LOG_FILE"
nohup proot-distro login "$CONTAINER" -- \
    "$AGENT" --secret-path "$SECRET_PATH" --socket-path "$SOCKET_PATH" \
    >> "$LOG_FILE" 2>&1 < /dev/null &

sleep 2
if ! pgrep -f '[p]layit --secret-path /root/.config/playit_gg/playit.toml' >/dev/null 2>&1; then
    printf '%s\n' "Playit agent did not remain running; inspect the private phone log." >&2
    exit 1
fi
