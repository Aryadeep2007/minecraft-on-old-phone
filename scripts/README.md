# Scripts

## Available scripts

| Script | Purpose | Verification |
|---|---|---|
| [`start.sh`](start.sh) | Start Paper with the configured heap cap | Reached `Done` on the target phone |
| [`termux-boot-start-server.sh`](termux-boot-start-server.sh) | Acquire a wake lock, restore SSH, and start Paper after Android boot | Shell syntax and duplicate-process guard verified manually; actual reboot is pending |

Scripts must not contain credentials or private phone details. See the [24/7 reliability guide](../docs/05-24-7-reliability.md) before installing the boot script.
