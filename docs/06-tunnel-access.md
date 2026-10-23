# 06 — Internet tunnel access

**Status: In progress.** The phone is ARM64 (`aarch64`). The official Playit Linux ARM64 agent and matching CLI v1.0.10 were downloaded into the existing Alpine PRoot container; both SHA-256 hashes matched the [official release page](https://github.com/playit-cloud/playit-agent/releases/tag/v1.0.10). The claim flow succeeded and the account is verified. The operator created a Java TCP tunnel targeting `127.0.0.1:25565` and disabled Playit's `Allow IPv6` option. DNS advertised a public Java port, a TCP connection succeeded, and a Minecraft status handshake returned Paper 1.21.11 with one player online (maximum six). One `SessionNotSetup` warning occurred at startup, then logs remained quiet for 10 seconds; the successful handshake verifies forwarding at that time. A separate Termux:Boot hook was installed, syntax-checked, and manually launched; the agent remained running after its SSH launch session ended and the public TCP tunnel remained reachable. A phone reboot has not yet been tested with Playit. Do not publish the endpoint or assigned port in this repository. The earlier IPv6 failure matched the [agent repository issue #194](https://github.com/playit-cloud/playit-agent/issues/194). The secret config remains on the phone with mode `600`.

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

The v1.0.10 release separates the daemon (`playit`) from its account-claim CLI (`playit-cli`). The CLI's `setup` command could not attach to the daemon socket in this PRoot environment. The verified workaround used `playit-cli claim generate`, `playit-cli claim url`, and `playit-cli claim exchange`, capturing the returned key locally and storing it in the daemon's private `secret_key` TOML file with permissions `600`. Never print or commit that key. Before account email verification, the agent repeatedly lost its control session. After the account was verified, the agent loaded the configured Java tunnel; public forwarding was then confirmed with a Minecraft status handshake.

## Tunnel status

- [x] ARM64 agent download, checksum verification, and help output tested in Alpine PRoot.
- [x] Claim the agent without publishing its device credential.
- [x] Verify the Playit account email and confirm that the agent connects.
- [x] Create a Java TCP tunnel in the Playit account.
- [x] Disable Playit's IPv6 option and confirm the unreachable IPv6 relay error stops in a short run.
- [x] Confirm the configured local target is `127.0.0.1:25565` and test public TCP forwarding with both a TCP connection and Minecraft status handshake.
- [x] Install `scripts/termux-boot-start-playit.sh` as a separate executable in `~/.termux/boot/`, syntax-check it, manually launch it, and confirm public Java TCP reachability after the SSH launch session ends.
- [ ] Reboot the phone and confirm Termux:Boot starts the Playit agent and the Java tunnel becomes reachable after Paper is ready.
- [ ] Confirm authentication and whitelist protections before sharing any public game address.
- [ ] Select and test the Bedrock transport and its exact required ports.

The live Paper Geyser plugin is currently configured for RakNet on UDP `19132`. Geyser's separate NetherNet test only verified standalone startup in Alpine; it was not connected to Paper or tested with a player. Playit's [Bedrock guidance](https://playit.gg/support/minecraft-bedrock-nethernet/) describes the current transition and says a TCP/UDP tunnel is required for NetherNet. Playit's agent v1.0.12 is a pre-release that adds a NetherNet tunnel type; do not assume that a working Java tunnel proves Bedrock compatibility. Re-check current official guidance before selecting a Bedrock tunnel or exposing it.

## Start the agent after Android boots

The repository includes a separate Termux:Boot hook for Playit. It uses the already linked agent in Alpine PRoot, leaves the credential in the Alpine private config, prevents duplicate processes, redirects diagnostic output to a mode-`600` file under Termux home, and never prints that log. It has been manually tested after installation; a full phone reboot test remains pending. Install it alongside the existing Paper boot hook (do not replace the Paper hook):

```powershell
scp -P 8022 scripts/termux-boot-start-playit.sh <TERMUX_USER>@<PHONE_LAN_IP>:/data/data/com.termux/files/home/.termux/boot/start-playit
ssh -p 8022 <TERMUX_USER>@<PHONE_LAN_IP> "chmod 700 ~/.termux/boot/start-playit && sh -n ~/.termux/boot/start-playit && ~/.termux/boot/start-playit"
```

Use the private Wi-Fi address currently shown in Android settings. Run this while connected locally and before relying on public access. The hook assumes the installed PRoot distro is named `alpine-musl-test` and that the agent and private config use the paths shown in the script. Confirm those local paths before adapting it for another phone. After launching, test Java connectivity, disconnect SSH, and confirm the tunnel still works. Complete a controlled reboot check before treating the agent as persistent. The log is stored only on the phone at `~/.local/var/log/playit-agent.log`; it may contain connection metadata, so do not publish or paste it.

## Security

An active game tunnel makes its configured local service reachable through a public endpoint. Do not start or share a public tunnel until the offline-mode login and whitelist behavior has been verified. Never tunnel SSH, RCON, or the dashboard. Keep Playit device credentials and account tokens on the phone and out of GitHub. Share only the public game endpoint with intended players, and remember that offline-mode usernames are not authenticated by Mojang.
