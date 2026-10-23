# 06 — Internet tunnel access

**Status: In progress.** The phone is ARM64 (`aarch64`). The official Playit Linux ARM64 agent and matching CLI v1.0.10 were downloaded into the existing Alpine PRoot container; both SHA-256 hashes matched the [official release page](https://github.com/playit-cloud/playit-agent/releases/tag/v1.0.10). The claim flow succeeded and the agent connected with zero tunnels, but Playit reports the account as `email_not_verified`. The agent was stopped after this check; its secret config remains on the phone with mode `600`. No public tunnels have been created or tested.

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

Only continue if `sha256sum -c` reports `OK`. The agent does not accept `--version`; the release tag and verified checksum establish which binary was installed. The CLI provides account-claim commands. Do not pass a secret on the command line or save one in this repository.

The v1.0.10 release separates the daemon (`playit`) from its account-claim CLI (`playit-cli`). The CLI's `setup` command could not attach to the daemon socket in this PRoot environment. The verified workaround used `playit-cli claim generate`, `playit-cli claim url`, and `playit-cli claim exchange`, capturing the returned key locally and storing it in the daemon's private `secret_key` TOML file with permissions `600`. Never print or commit that key. The daemon connected, but the account was not email-verified and repeatedly lost its control session; it was stopped until verification is completed.

## Tunnel status

- [x] ARM64 agent download, checksum verification, and help output tested in Alpine PRoot.
- [x] Claim the agent without publishing its device credential.
- [ ] Verify the Playit account email so the agent control session can remain active.
- [ ] Create and test the Java TCP tunnel to Paper on local port `25565`.
- [ ] Confirm authentication and whitelist protections before sharing any public game address.
- [ ] Select and test the Bedrock transport and its exact required ports.

The live Paper Geyser plugin is currently configured for RakNet on UDP `19132`. Geyser's separate NetherNet test only verified standalone startup in Alpine; it was not connected to Paper or tested with a player. Playit's [Bedrock guidance](https://playit.gg/support/minecraft-bedrock-nethernet/) describes the current transition and says a TCP/UDP tunnel is required for NetherNet. Playit's agent v1.0.12 is a pre-release that adds a NetherNet tunnel type; do not assume that a working Java tunnel proves Bedrock compatibility. Re-check current official guidance before selecting a Bedrock tunnel or exposing it.

## Security

An active game tunnel makes its configured local service reachable through a public endpoint. Do not start or share a public tunnel until the offline-mode login and whitelist behavior has been verified. Never tunnel SSH, RCON, or the dashboard. Keep Playit device credentials and account tokens on the phone and out of GitHub. Share only the public game endpoint with intended players, and remember that offline-mode usernames are not authenticated by Mojang.
