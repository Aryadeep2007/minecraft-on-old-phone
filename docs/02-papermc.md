# 2. PaperMC

**Status: In progress.** Paper 1.21.11 stable build 132 starts under Java 21 with a 1.5 GiB maximum heap. A detached Termux start reached `Done`, and TCP port 25565 was reachable from the setup computer on the local network. Gameplay, sustained performance, Termux:Boot, and wake-lock behavior remain unverified.

## Goal

Run a small Paper server on Termux with a conservative heap limit, then verify that it starts on the phone's Java runtime.

## Version selection

The agreed Termux runtime is Java 21. Paper's current requirements list Java 21 for Minecraft 1.20 through 1.21.11 and Java 25 for Paper 26.1 and newer. This guide therefore uses the latest stable Paper build in the Java 21-compatible 1.21.11 line. Recheck Java requirements before changing versions.

Paper reported at startup that stable 26.3 was six releases newer than 1.21.11. The project stays on 1.21.11 to match the agreed Java 21 runtime; Java clients must use a compatible Minecraft version unless a later phase adds and verifies a compatibility plugin.

- [Paper Java requirements](https://docs.papermc.io/paper/getting-started/)
- [Paper downloads service](https://docs.papermc.io/misc/downloads-service/)

## Download and verify Paper

Create a dedicated server directory on the phone, then download the stable build and verify the checksum published by Paper's API:

```sh
mkdir -p ~/minecraft-server
cd ~/minecraft-server
curl -fL --retry 2 \
  -H 'User-Agent: minecraft-on-old-phone/0.1 (https://github.com/Aryadeep2007/minecraft-on-old-phone)' \
  -o paper.jar.tmp \
  'https://fill-data.papermc.io/v1/objects/5ffef465eeeb5f2a3c23a24419d97c51afd7dbb4923ff42df9a3f58bba1ccfba/paper-1.21.11-132.jar'
printf '%s  %s\n' '5ffef465eeeb5f2a3c23a24419d97c51afd7dbb4923ff42df9a3f58bba1ccfba' 'paper.jar.tmp' | sha256sum -c -
mv paper.jar.tmp paper.jar
```

This checksum and URL identify Paper 1.21.11 stable build 132 as checked on 2026-10-23. Before replacing an existing server JAR, back it up and verify the new download first.

## First startup and heap

The start script in this repository uses a 512 MiB initial heap and a 1.5 GiB maximum heap. Copy `scripts/start.sh` into the phone's `~/minecraft-server` directory, where `paper.jar` lives, then launch it from Termux:

```sh
cd ~/minecraft-server
chmod 700 start.sh
./start.sh
```

The script expects `paper.jar` in the same directory and changes into that directory before starting Paper. Keep the script's line endings as LF on Termux.

To keep Paper running after an SSH command or terminal session exits, launch it detached from the server directory:

```sh
cd ~/minecraft-server
mkdir -p logs
nohup ./start.sh >> logs/console.log 2>&1 < /dev/null &
```

Check `tail -n 30 logs/console.log` for Paper's `Done` message. On the target phone, running Paper in the foreground of an interactive SSH session stopped it when that session ended. The detached command above was verified: Paper stayed running after the SSH command completed and port 25565 accepted a local TCP connection. This does not yet configure Android boot startup or prevent Android from stopping Termux.

On first launch, Paper writes `eula.txt` and stops while `eula=false`. Read the [Minecraft EULA](https://aka.ms/MinecraftEULA). Change the setting to `eula=true` only if the server operator agrees to the terms, then start Paper again. Never commit `eula.txt` or other live server files.

## Verified result

Verified on the target OPPO A57 using OpenJDK 21.0.13 (`aarch64`):

| Check | Result |
|---|---|
| Paper build | `1.21.11-132`, stable |
| JAR size | 54,846,016 bytes (about 52.3 MiB) |
| SHA-256 | `5ffef465eeeb5f2a3c23a24419d97c51afd7dbb4923ff42df9a3f58bba1ccfba` |
| Bootstrap | Java 21 loaded Paper and completed remapping in about 70 seconds |
| EULA | Local `eula.txt` was set to `eula=true` for the startup verification; live file stays on the phone |
| Full startup | Reached `Done (161.479s)` and created the Overworld, Nether, and End |
| Shutdown | `stop` saved all dimensions; the Paper process exited |
| Persistent server | Detached start remained alive after SSH returned; local TCP port 25565 accepted a connection |
| Start script | `./start.sh` launched Paper 1.21.11 with `-Xms512M -Xmx1536M`; reached `Done (103.466s)` and shut down cleanly |

During startup, Termux emitted JLine and OSHI/JNA warnings about missing Linux libraries (`libutil.so.1` and `libudev`). Netty could not read a hardware MAC address and used random bytes; Spark's optional async-profiler could not load `libdl.so.2`. Paper still reached `Done` and shut down cleanly. Player connections and sustained performance are not verified yet.

## Current server settings

After the first clean shutdown, `view-distance` was changed from the generated default of 10 to the planned value of 6. The live `server.properties` remains on the phone and is not committed. The following values were read back after the edit:

| Property | Current value | Note |
|---|---:|---|
| `view-distance` | `6` | Applied on the phone; gameplay performance not yet measured |
| `simulation-distance` | `6` | Applied on the phone; gameplay performance not yet measured |
| `online-mode` | `false` | AuthMe and PacketEvents are enabled for offline-mode authentication; see the authentication guide |
| `white-list` | `true` | The operator's name is on the live whitelist; private player names stay out of Git |
| `max-players` | `6` | Configured for the planned small group; concurrent-player performance not yet tested |

Offline mode does not authenticate usernames by itself. Keep AuthMe enabled, require password login for non-premium names, whitelist only trusted players, and do not expose the server through a public tunnel until login and whitelist behavior have been tested.

## Security

Keep the server directory, world, JAR, logs, and live configuration on the phone and out of Git. Do not expose RCON or management services publicly. Use backups before upgrading Paper or changing world formats.
