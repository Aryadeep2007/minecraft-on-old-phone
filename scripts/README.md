# Scripts

## Available scripts

| Script | Purpose | Verification |
|---|---|---|
| [`start.sh`](start.sh) | Start Paper with the configured heap cap | Reached `Done` on the target phone |
| [`termux-boot-start-server.sh`](termux-boot-start-server.sh) | Acquire a wake lock, restore SSH, and start Paper after Android boot | Shell syntax, duplicate-process guard, and controlled phone reboot verified |
| [`termux-boot-start-playit.sh`](termux-boot-start-playit.sh) | Start the Playit agent from its private Alpine PRoot configuration after Android boots | Installed, syntax-checked, and manually launched; public Java tunnel remained reachable after SSH disconnected. Phone reboot verification is pending |

Scripts must not contain credentials or private phone details. See the [24/7 reliability guide](../docs/05-24-7-reliability.md) before installing the boot script.
