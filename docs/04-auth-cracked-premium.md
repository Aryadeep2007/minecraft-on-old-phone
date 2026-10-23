# 04 — Java authentication and offline accounts

**Status: In progress.** AuthMe 6.0.1 and PacketEvents 2.14.0 are installed and verified as loaded on Paper 1.21.11. The server is still in online mode and the whitelist is still disabled. Authentication settings and Java client logins have not yet been tested.

## Goal

Require password registration for offline-mode Java players, let enrolled premium Java players bypass the password prompt, and restrict access with the whitelist. Bedrock authentication remains handled through Geyser and Floodgate.

## Why this plugin combination

This guide uses AuthMe's built-in premium bypass with PacketEvents 2.x. Current FastLogin documentation lists AuthMe 5.x for its AuthMe hook; this project uses AuthMe 6.0.1 and does not install FastLogin. AuthMe's direct-server premium bypass requires an offline-mode Paper backend and PacketEvents 2.x. Premium enrollment is opt-in per player after they first register or log in.

## Install and verify the plugins

The phone used Paper 1.21.11 on Java 21. Stop Paper before installing plugins. These commands download official release assets, check the published SHA-256 digests, and place the JARs in the server's `plugins/` directory:

```sh
cd ~/minecraft-server
mkdir -p .plugin-install-tmp
curl -fL 'https://github.com/AuthMe/AuthMeReloaded/releases/download/6.0.1/AuthMe-6.0.1-Paper.jar' -o .plugin-install-tmp/AuthMe-6.0.1-Paper.jar
curl -fL 'https://github.com/retrooper/packetevents/releases/download/v2.14.0/packetevents-spigot-2.14.0.jar' -o .plugin-install-tmp/packetevents-spigot-2.14.0.jar
echo '7704335e9e73a634d9d926344f77897f4c74f78f82453a59f5aa0f8d2722450a  .plugin-install-tmp/AuthMe-6.0.1-Paper.jar' | sha256sum -c -
echo '060087c58ec268eae7dd0eb1f17ac3bea1eaadda1693414141ff64e506091bd7  .plugin-install-tmp/packetevents-spigot-2.14.0.jar' | sha256sum -c -
test ! -e plugins/AuthMe-6.0.1-Paper.jar
test ! -e plugins/packetevents-spigot-2.14.0.jar
mv .plugin-install-tmp/AuthMe-6.0.1-Paper.jar plugins/
mv .plugin-install-tmp/packetevents-spigot-2.14.0.jar plugins/
rmdir .plugin-install-tmp
```

Only move files after both checksum checks report `OK`. If a destination file already exists, stop and inspect it rather than overwriting it.

Start Paper with `./start.sh` and confirm the startup log lists `AuthMe (6.0.1)`, `packetevents (2.14.0)`, and ends with `Done`. On the first AuthMe startup, Paper downloads AuthMe's declared libraries and creates `plugins/AuthMe/` plus its SQLite database. The first run on the OPPO took about 5 minutes 45 seconds; later starts may be faster because those libraries are cached.

## Verified on the target phone

- Both JARs matched the SHA-256 values published on their official GitHub releases.
- Paper listed AuthMe 6.0.1 and PacketEvents 2.14.0 in its plugin initialization list.
- AuthMe downloaded and loaded its declared libraries, initialized SQLite, and reported that it enabled successfully.
- PacketEvents loaded and enabled successfully.
- Paper reached `Done` and was stopped with a graceful interrupt; the log confirmed all dimensions were saved.
- Existing Geyser, Floodgate, and ViaVersion also loaded. Geyser started UDP port 19132.
- No player authentication flow has been tested yet. `online-mode=true` and `white-list=false` were left unchanged during this install and startup check.

## Next configuration work

Do not switch the server to offline mode until AuthMe's settings have been reviewed. The next authentication step must configure AuthMe's premium bypass (`settings.enablePremium: true`), keep PacketEvents installed, change the server to offline mode, enable the whitelist, and restart. Back up the world and live configs first. Then test registration and login with a non-premium test account, premium verification with an enrolled premium account, whitelist enforcement, and Bedrock join behavior before exposing the server through a tunnel.

For premium bypass, players opt in individually after registration/login with `/premium`; AuthMe verifies their Mojang account and stores the enrollment. Without PacketEvents, AuthMe fails closed and uses normal password authentication.

## Security

Offline mode does not verify Java account ownership by itself. AuthMe and the whitelist must be configured before offline mode is enabled. Use unique, strong passwords, do not share accounts, and back up AuthMe's database. Never publish the live AuthMe configuration, database, player data, logs, SSH key, or server files. Keep RCON and any dashboard private.

## Sources

- [AuthMe 6.0.1 release and Paper JAR checksum](https://github.com/AuthMe/AuthMeReloaded/releases/tag/6.0.1)
- [AuthMe premium bypass requirements and enrollment](https://github.com/AuthMe/AuthMeReloaded/blob/master/docs/premium.md)
- [PacketEvents 2.14.0 release and Spigot JAR checksum](https://github.com/retrooper/packetevents/releases/tag/v2.14.0)
- [FastLogin compatibility information](https://github.com/TuxCoding/FastLogin/blob/main/README.md)
