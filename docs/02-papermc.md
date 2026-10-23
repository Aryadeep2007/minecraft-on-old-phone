# 2. PaperMC

**Status: In progress.** Paper 1.21.11 stable build 132 is installed and its first startup reached the EULA gate. The server has not completed a full startup; the EULA remains `false` until the operator reviews and accepts it.

## Goal

Run a small Paper server on Termux with a conservative heap limit, then verify that it starts on the phone's Java runtime.

## Version selection

The agreed Termux runtime is Java 21. Paper's current requirements list Java 21 for Minecraft 1.20 through 1.21.11 and Java 25 for Paper 26.1 and newer. This guide therefore uses the latest stable Paper build in the Java 21-compatible 1.21.11 line. Recheck Java requirements before changing versions.

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
| EULA | `eula.txt` created with `eula=false`; startup stopped as expected |
| Persistent server | Not running; full startup awaits the operator's EULA decision |

During bootstrap, Termux emitted JLine and OSHI/JNA native-library warnings about missing Linux libraries (`libutil.so.1` and `libudev`). Paper continued through server remapping and reached the EULA check. Full startup and gameplay still need verification.

## Security

Keep the server directory, world, JAR, logs, and live configuration on the phone and out of Git. Do not expose RCON or management services publicly. Use backups before upgrading Paper or changing world formats.
