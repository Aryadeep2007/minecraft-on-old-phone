# 07 — Private web dashboard

**Status: In progress.** The Flask and Waitress dashboard, login page, server controls, whitelist forms, RCON console, and world-backup action are implemented in this repository. Source-level checks are complete. Deployment on the phone and end-to-end verification remain pending. The dashboard is designed to listen only on phone loopback and to be reached from a trusted computer through SSH local forwarding.

## What it provides

- Sign-in with a separate dashboard password, session expiry, and temporary lockout after repeated failed attempts.
- Paper status, start/stop/restart, Java whitelist add/remove, RCON console, and compressed backups of `world`, `world_nether`, and `world_the_end`.
- CSRF checks for form actions, secure response headers, a loopback-only RCON client, and a loopback-only web listener.

Backups contain world folders only. They use additional phone storage and are not downloaded by the dashboard. There is no restore or backup-retention feature yet. RCON console access is equivalent to administrator access in the game.

## Install on Termux

Clone this repository in Termux (or copy the project there), then install the dashboard's Python dependencies in an isolated virtual environment:

```sh
pkg install python
cd ~/minecraft-on-old-phone
python -m venv .venv
. .venv/bin/activate
pip install -r dashboard/requirements.txt
cp dashboard/.env.example .env
```

Edit `.env` on the phone and replace the three secret placeholders. Generate separate random values locally, for example with `python -c 'import secrets; print(secrets.token_urlsafe(48))'`. Use one value for `FLASK_SECRET_KEY`, another for `DASHBOARD_PASSWORD`, and a third for `RCON_PASSWORD`. Keep the dashboard password distinct from Minecraft account passwords. Set file permissions after editing:

```sh
chmod 600 .env
```

Use the actual server and backup paths if they differ from the example. The application refuses to start when required secrets are missing or when `RCON_HOST` is not loopback.

## RCON prerequisite

The live Paper configuration was inspected over key-authenticated SSH on 2026-10-24. It had `enable-rcon=false`, `rcon.port=25575`, a blank `server-ip`, and no explicit `rcon.ip` entry. Paper documents that blank `server-ip` binds the game server to all interfaces ([server properties](https://docs.papermc.io/paper/reference/server-properties/)). Inspection of the installed Paper 1.21.11 server JAR confirmed that it recognizes the separate `rcon.ip` property.

RCON was then enabled with `rcon.ip=127.0.0.1` and a newly generated private password. The existing blank `server-ip` was preserved, so the game listener stayed available on loopback and Wi-Fi. A private copy of the previous properties file was kept on the phone before the update. The server was shut down gracefully and restarted.

Verification from Termux on the phone confirmed that the game port accepted connections at both `127.0.0.1` and the phone's Wi-Fi address. RCON accepted connections and authentication at `127.0.0.1`, refused the phone's Wi-Fi address, and returned a response to the read-only `list` command. The password and command response were not printed. The dashboard still needs to be installed and configured with this private RCON password before its controls can be used. Never tunnel or port-forward RCON.

## Start and connect

Start the dashboard on the phone:

```sh
cd ~/minecraft-on-old-phone
sh scripts/start-dashboard.sh
```

The production Waitress server binds to `127.0.0.1:8765`; it does not listen on the Wi-Fi interface. Keep that Termux process running. From a trusted computer with SSH access to the phone, open a local forward in a terminal:

```sh
ssh -N -L 8765:127.0.0.1:8765 -p 8022 <TERMUX_USER>@<PHONE_LAN_IP>
```

Then browse to `http://127.0.0.1:8765`. Leave the SSH command running while using the page. Replace placeholders only in the command; never record your private address or username in this repository. Stop the forward with Ctrl+C when finished. If port 8765 is already occupied on the computer, use another local port, for example `-L 18765:127.0.0.1:8765`, and open `http://127.0.0.1:18765`.

## Verification checklist

- [ ] Confirm the dashboard process starts on the phone with private `.env` permissions.
- [ ] Confirm it is listening only on `127.0.0.1:8765`.
- [ ] Confirm SSH port forwarding opens the sign-in page from the computer.
- [ ] Confirm an incorrect password is rejected and the correct password opens the panel.
- [ ] Confirm server actions, whitelist, console, and backup behavior after RCON is enabled safely.
- [ ] Confirm the dashboard is not reachable through the Java or Bedrock game tunnel.

## Security

Never expose port `8765` or RCON `25575` through Playit, a router port-forward, or a public tunnel. The SSH forward encrypts the computer-to-phone connection; dashboard HTTP is intentionally used only inside that encrypted local forward. Protect the computer and SSH key, use unique secrets, keep `.env` out of Git, and do not paste credentials, logs, player data, or live configs into issues. The dashboard's general RCON command form carries full operator privileges.
