# 04 — Java authentication and offline accounts

**Status: In progress.** AuthMe 6.0.1 and PacketEvents 2.14.0 are installed on Paper 1.21.11. A read-only inspection confirmed AuthMe registration and required authentication are enabled, the server is in offline mode, the whitelist is on, and the operator's Java name is present in it. The operator confirmed that a non-premium Java player authenticated with an AuthMe password and joined. First-time registration was not separately confirmed, and premium verification remains untested.

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
- A later read-only check confirmed `online-mode=false`, `white-list=true`, and the operator's whitelist entry. AuthMe registration is enabled and `force: true` requires authentication before players can play. The operator's exact name is intentionally omitted from this public guide.
- Paper's `enforce-whitelist` property is currently `false`. Paper documents this as controlling whether players who are not on the whitelist are kicked; the separate `white-list=true` setting remains enabled and is the join gate. No live setting was changed during this inspection.
- The operator confirmed a successful non-premium Java password login and join. First-time registration was not separately confirmed. During the earlier plugin-install check, the then-current `online-mode=true` and `white-list=false` settings were left unchanged; they were changed in a later configuration step.

## Join the local server

With Paper running, add a Java name to the whitelist in the server console:

```text
whitelist add <YOUR_JAVA_USERNAME>
```

From a Java client on the same Wi-Fi network, connect to `<PHONE_LAN_IP>:25565` using Minecraft 1.21.11. A non-premium Java profile must use the same name that was added to the whitelist. On first join, register with `/register <strong-password> <strong-password>`; on later joins, use `/login <password>`. Use a unique password, and do not put it in chat, screenshots, logs, or public files.

This phone's operator name was added successfully through the console (`Added ... to the whitelist`) and is present in the live whitelist file. The exact player name and phone address are intentionally omitted from this public guide.

## Next configuration work

The live server is in offline mode with AuthMe premium bypass (`settings.enablePremium: true`), PacketEvents installed, and the whitelist enabled. Non-premium password login and joining are verified. Confirm first-time registration separately if it has not already occurred, and test premium account enrollment if one is available. Also check whitelist behavior and Bedrock join behavior before exposing the server through a tunnel.

For premium bypass, players opt in individually after registration/login with `/premium`; AuthMe verifies their Mojang account and stores the enrollment. Without PacketEvents, AuthMe fails closed and uses normal password authentication.

## Security

Offline mode does not verify Java account ownership by itself. AuthMe and the whitelist must be configured before offline mode is enabled. Use unique, strong passwords, do not share accounts, and back up AuthMe's database. Never publish the live AuthMe configuration, database, player data, logs, SSH key, or server files. Keep RCON and any dashboard private.

## Sources

- [AuthMe 6.0.1 release and Paper JAR checksum](https://github.com/AuthMe/AuthMeReloaded/releases/tag/6.0.1)
- [AuthMe premium bypass requirements and enrollment](https://github.com/AuthMe/AuthMeReloaded/blob/master/docs/premium.md)
- [PacketEvents 2.14.0 release and Spigot JAR checksum](https://github.com/retrooper/packetevents/releases/tag/v2.14.0)
- [FastLogin compatibility information](https://github.com/TuxCoding/FastLogin/blob/main/README.md)
