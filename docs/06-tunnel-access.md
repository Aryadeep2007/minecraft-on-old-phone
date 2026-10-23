# 06 — Internet tunnel access

**Status: In progress.** The phone is ARM64 (`aarch64`). The official Playit Linux ARM64 agent v1.0.10 was downloaded into the existing Alpine PRoot container. Its SHA-256 matched the hash published on the [official release page](https://github.com/playit-cloud/playit-agent/releases/tag/v1.0.10), and `playit --help` ran successfully. The agent is not yet linked to an account, and no public tunnels have been created or tested.

## Goal

Allow remote players to connect through a tunnel when the ISP uses CGNAT, without router port forwarding. The intended services are Java over TCP and Bedrock over the transport supported by the selected Geyser and tunnel versions.

## Verified agent installation

The official release currently provides a Linux ARM64 binary. This phone runs Android/Bionic, so this project placed the Linux agent inside the already tested Alpine PRoot container rather than assuming a Linux binary runs directly in Termux.

From an Alpine PRoot shell, download and verify the v1.0.10 binary before installing it:

```sh
mkdir -p /root/.local/bin
cd /root/.local/bin
wget -O playit.download https://github.com/playit-cloud/playit-agent/releases/download/v1.0.10/playit-linux-aarch64
printf '4c0db3e7b3a8158e249441c2f0b73f54e83429395890c7b1ca45fd7a6303d763  playit.download\n' | sha256sum -c -
chmod 700 playit.download
mv playit.download playit
./playit --help
```

Only continue if `sha256sum -c` reports `OK`. The agent does not accept `--version`; the release tag and verified checksum establish which binary was installed. Do not pass a secret on the command line or save one in this repository.

## Tunnel status

- [x] ARM64 agent download, checksum verification, and help output tested in Alpine PRoot.
- [ ] Link the agent to a Playit account without publishing its device credential.
- [ ] Create and test the Java TCP tunnel to Paper on local port `25565`.
- [ ] Confirm authentication and whitelist protections before sharing any public game address.
- [ ] Select and test the Bedrock transport and its exact required ports.

The live Paper Geyser plugin is currently configured for RakNet on UDP `19132`. Geyser's separate NetherNet test only verified standalone startup in Alpine; it was not connected to Paper or tested with a player. Playit's [Bedrock guidance](https://playit.gg/support/minecraft-bedrock-nethernet/) describes the current transition and says a TCP/UDP tunnel is required for NetherNet. Playit's agent v1.0.12 is a pre-release that adds a NetherNet tunnel type; do not assume that a working Java tunnel proves Bedrock compatibility. Re-check current official guidance before selecting a Bedrock tunnel or exposing it.

## Security

An active game tunnel makes its configured local service reachable through a public endpoint. Do not start or share a public tunnel until the offline-mode login and whitelist behavior has been verified. Never tunnel SSH, RCON, or the dashboard. Keep Playit device credentials and account tokens on the phone and out of GitHub. Share only the public game endpoint with intended players, and remember that offline-mode usernames are not authenticated by Mojang.
