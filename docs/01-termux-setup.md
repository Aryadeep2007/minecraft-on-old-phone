# 1. Termux setup

**Status: In progress.** SSH access and the phone architecture/memory check are verified. Java installation and runtime verification remain to be completed.

## Goal

Prepare Termux for administration, establish key-based SSH access, and inspect the phone before installing the server.

## Requirements

- Termux installed from F-Droid.
- The phone and administration computer connected to the same trusted Wi-Fi network for initial SSH access.
- OpenSSH client on the computer.

## Install OpenSSH in Termux

Open Termux on the phone and run:

```sh
pkg update && pkg install openssh
```

Start the SSH daemon and identify the Termux account:

```sh
sshd
whoami
```

Termux OpenSSH listens on port `8022` by default. Find the phone's local Wi-Fi address in Android **Settings → Wi-Fi → connected network details** if a network-interface query in Termux is denied.

## Configure key-based access

On the administration computer, create a dedicated key pair (example for Windows OpenSSH):

```powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\minecraft_phone" -C "minecraft-phone-termux"
```

Copy the contents of `minecraft_phone.pub`. In Termux, append that **public** key to `authorized_keys`:

```sh
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys <<'EOF'
<PASTE_THE_PUBLIC_KEY_LINE_HERE>
EOF
chmod 600 ~/.ssh/authorized_keys
```

Connect from the computer, replacing both placeholders with the values shown by Termux and Android Settings:

```sh
ssh -i ~/.ssh/minecraft_phone -p 8022 <TERMUX_USER>@<PHONE_LAN_IP> "uname -m && free -h"
```

Never copy the private key to the phone or repository. Do not expose SSH to the public internet; keep initial administration on a trusted local network.

## Verification

Verified on the target OPPO A57 (4 GB RAM; Android version not recorded):

| Check | Result |
|---|---|
| SSH transport | Key-based login succeeded on port `8022` |
| Architecture | `aarch64` (ARM64) |
| Memory reported by `free -h` | 3.7 GiB total; 2.0 GiB used; 176 MiB free; 1.5 GiB available |
| Swap reported by `free -h` | 3.5 GiB total; 1.0 GiB used; 2.5 GiB free |

These values are a point-in-time reading and will change as Android apps use memory. OpenJDK 21 is not installed or verified yet.

## Security

Use SSH keys instead of password login. Keep the private key on the administration computer and out of Git. Use a trusted local network during setup; do not forward port `8022` from the router or expose it through a public tunnel.
