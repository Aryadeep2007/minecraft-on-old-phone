# 3. Bedrock connectivity with Geyser and Floodgate

**Status: In progress.** Geyser, Floodgate, and ViaVersion have loaded on the target OPPO A57 under Java 21 and Paper 1.21.11. Geyser started its current RakNet listener on UDP 19132, and its authentication mode is set to Floodgate. A Bedrock client has not joined yet, and the listener has not been exposed through a tunnel.

## Goal

Let Bedrock Edition players join the Paper server. Geyser translates Bedrock connections to the Java protocol; Floodgate lets Bedrock players join without a paid Java Edition account. Because current Geyser emulates the current Java client version, ViaVersion is needed for the older Paper 1.21.11 server.

Geyser's current supported versions and Java requirement can change. Check the official [supported versions](https://geysermc.org/wiki/geyser/supported-versions/) page before updating plugins.

## Install the plugins

Install the Paper/Spigot plugin artifacts in the phone's `~/minecraft-server/plugins/` directory. Paper must be stopped before adding or replacing plugin JARs.

The following official builds were installed and SHA-256 verified on 2026-10-23:

| Plugin | Version/build | Installed JAR | SHA-256 |
|---|---|---|---|
| Geyser-Spigot | 2.12.0, build 1269 | `Geyser-Spigot.jar` | `6537e1fb6ef1e115172653ca42c0f9c2e38d07ca2415142bb5e0fb9aeecd1e07` |
| Floodgate-Spigot | 2.2.5, build 141 | `floodgate-spigot.jar` | `21570aff9ce17d6983928e8552777760e1ede5050026b04c686b0ae112e6fd7e` |
| ViaVersion | 5.12.1 stable | `ViaVersion-5.12.1.jar` | `bab94b846e1d2bf516c070562d0271b32382afd41870bf0d3a7993b73a36f791` |

Use the official [Geyser download API](https://geysermc.org/wiki/api/downloads.geysermc.org/download-latest/), [Geyser downloads](https://geysermc.org/download), and [ViaVersion releases](https://hangar.papermc.io/ViaVersion/ViaVersion/versions) to check current versions. Download into temporary `.tmp` files, verify the SHA-256 published by the source, then rename each file into `plugins/`. Never overwrite a plugin JAR without first checking the version and preserving a rollback copy.

Geyser's current Paper setup guide says servers older than Java Edition 26.3 need ViaVersion. The Paper 1.21.11-compatible ViaVersion build above loaded successfully and detected server protocol 1.21.11 (774).

## Configure Floodgate authentication

After installing all three plugins, start Paper once. The plugins create their configuration directories under `plugins/`. Stop Paper cleanly, then set `java.auth-type` in `plugins/Geyser-Spigot/config.yml` to `floodgate`:

```yaml
java:
  auth-type: floodgate
```

Floodgate automatically provides its generated key to Geyser when both plugins run on the same Paper server. Keep `plugins/floodgate/key.pem` private; never publish it. The phone's Geyser configuration currently has `auth-type: floodgate`.

## Start and verify

Start Paper with the phone's `./start.sh`. Confirm the log reports Floodgate and ViaVersion enabled, Geyser loaded, and Geyser started its Bedrock listener. Then stop Paper with `stop` and let it save the world.

On the target phone, the plugins loaded and the log reported:

```text
ViaVersion detected server version: 1.21.11 (774)
Started Geyser on UDP port 19132
Geyser Done (39.585s)
Paper Done (214.192s)
```

This verifies plugin startup and local UDP listener creation only. Bedrock and Java clients have not yet joined, external access has not been configured, and performance with players is untested.

## NetherNet and transport planning

The installed Geyser build warned that NetherNet support is not enabled. Geyser's current [NetherNet migration guidance](https://geysermc.org/blog/preparing-for-nethernet/) says Bedrock 26.60 is scheduled for October 27, 2026, after which Bedrock clients will require NetherNet. Built-in signaling uses TCP 19132 as well as UDP gameplay; using both NetherNet and RakNet also needs a separate UDP `webrtc-port`.

A dual-transport trial used `transport: both`, `port: 19132`, and `webrtc-port: 19133`. Geyser started the RakNet UDP listener, but NetherNet initialization failed with `Cannot identify the JVM's libc`. The Geyser JAR contains native builds for Linux glibc and musl, but no Android/Bionic build. The phone's config was restored to the previous `transport: raknet`, `port: 19132`, and `webrtc-port: 0` settings. NetherNet is not currently available in this direct Termux runtime. Do not advertise this server as compatible with future clients that require NetherNet until the runtime issue is resolved.

### Separate musl userland experiment

The first experiment used Debian 13 under Termux `proot-distro`. Debian reported glibc 2.41, but its OpenJDK 21 package repeatedly stopped during configuration with `proot warning: signal 11 received from process -1`. The Java security configuration remained under `.dpkg-new` filenames, and Geyser Standalone failed with `InternalError: Error loading java.security file` before startup.

An isolated Alpine 3.24.3 container provided a working alternative. Alpine's `openjdk21-jre-headless` 21.0.12 package uses musl on ARM64, matching a native build bundled by Geyser. The official Geyser Standalone 2.12.0 build 1269 was run with `-DgeyserTransport=nethernet` and a 512 MiB maximum heap. It reported `Transport set from system property: nethernet`, started built-in signaling, completed STUN discovery, and reached `Done (110.854s)`. The test process was stopped afterward. Paper remained stopped throughout.

This verifies Geyser Standalone startup with NetherNet under Alpine/musl only. The standalone test was not connected to Paper, did not use Floodgate authentication, and has not been tested with a Bedrock client or through a tunnel. Combined memory and performance with Paper are also unverified. The installed Paper Geyser plugin configuration remains on RakNet; do not switch production traffic until the backend and client path are tested.

For reference, the isolated test used:

```sh
proot-distro install alpine:3.24 --name alpine-musl-test
proot-distro login alpine-musl-test -- apk add --no-cache openjdk21-jre-headless
```

The Geyser Standalone JAR and its generated test config stayed on the phone and are not part of this repository.

Before exposing the service, choose a supported Bedrock transport and update the tunnel plan to match. Geyser's [Paper setup guide](https://geysermc.org/wiki/geyser/setup/) documents NetherNet, combined NetherNet/RakNet, and the required ports. Do not publicly expose unrelated services or share the Floodgate key.

## Security

Keep plugin JARs, generated plugin configs, Floodgate keys, player data, and logs on the phone and out of Git. A Bedrock tunnel will need the exact TCP/UDP ports for the selected Geyser transport; never expose RCON or the dashboard as part of that tunnel.
