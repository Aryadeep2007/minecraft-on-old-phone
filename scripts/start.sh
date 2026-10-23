#!/data/data/com.termux/files/usr/bin/sh
set -eu

cd "$(dirname "$0")"
exec java -Xms512M -Xmx1536M -jar paper.jar --nogui
