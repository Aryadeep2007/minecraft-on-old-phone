# 2. PaperMC

**Status: In progress.** Paper 1.21.11 stable build 132 completed its first full startup and was stopped cleanly. The phone's `view-distance` is now set to 6. Heap/view-distance performance and operational scripts remain to be verified.

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

The initial launch uses a 512 MiB initial heap and a 1.5 GiB maximum heap:

```sh
cd ~/minecraft-server
java -Xms512M -Xmx1536M -jar paper.jar --nogui
```

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
| Persistent server | Not left running after the verification boot |

During startup, Termux emitted JLine and OSHI/JNA warnings about missing Linux libraries (`libutil.so.1` and `libudev`). Netty could not read a hardware MAC address and used random bytes; Spark's optional async-profiler could not load `libdl.so.2`. Paper still reached `Done` and shut down cleanly. Player connections and sustained performance are not verified yet.

## Current server settings

After the first clean shutdown, `view-distance` was changed from the generated default of 10 to the planned value of 6. The live `server.properties` remains on the phone and is not committed. The following values were read back after the edit:

| Property | Current value | Note |
|---|---:|---|
| `view-distance` | `6` | Applied on the phone; gameplay performance not yet measured |
| `simulation-distance` | `10` | Left unchanged |
| `online-mode` | `true` | Authentication phase has not started |
| `white-list` | `false` | Whitelist phase has not started |
| `max-players` | `20` | Capacity has not been tuned or tested |

Do not set `online-mode=false` until the authentication plan is implemented and verified.

## Security

Keep the server directory, world, JAR, logs, and live configuration on the phone and out of Git. Do not expose RCON or management services publicly. Use backups before upgrading Paper or changing world formats.
