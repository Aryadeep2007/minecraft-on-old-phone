# 05 — Keep the server running

**Status: In progress.** Termux:Boot was installed from F-Droid and opened once. The operator confirms Android battery/background activity was set to allow Termux and Termux:Boot to run without restriction. The boot script in this repository is installed on the phone, passes `sh -n`, and was run manually: it acquired the Termux wake lock without starting duplicate Paper or SSH daemons. A full phone reboot, charging limits, and long-duration thermal behavior are not yet verified.

## Goal

Start Paper and SSH after the phone reboots, keep Termux's CPU available while the server is running, and reduce the chance Android stops the server in the background. A phone is not a dedicated server appliance: battery health, temperature, Android background limits, and available memory can still interrupt service.

## Install Termux:Boot

Install Termux:Boot from the same source as the Termux app. This phone uses the F-Droid build, so install the F-Droid Termux:Boot package. Open Termux:Boot once from the Android launcher after installation; this enables the app's boot receiver. Termux:Boot runs executable scripts from `~/.termux/boot/` after Android starts.

See the [official Termux:Boot instructions](https://github.com/termux/termux-boot#how-to-use) for installation and script behavior.

## Install the boot script

The repository script acquires a wake lock, starts `sshd` only if it is not already running, and launches Paper only if a Paper Java process is not already active. It appends server output to `~/minecraft-server/logs/console.log`.

From a computer that can SSH into the phone, copy and enable the script:

```powershell
scp -P 8022 scripts/termux-boot-start-server.sh <TERMUX_USER>@<PHONE_LAN_IP>:/data/data/com.termux/files/home/.termux/boot/start-minecraft
ssh -p 8022 <TERMUX_USER>@<PHONE_LAN_IP> "chmod 700 ~/.termux/boot/start-minecraft && sh -n ~/.termux/boot/start-minecraft"
```

Replace the placeholders with the Termux username and current private Wi-Fi address. Do not put either value in this repository. If the directory does not exist, create it in Termux first with `mkdir -p ~/.termux/boot`. Do not overwrite an existing boot script without reviewing it.

To run the script manually for a non-reboot check:

```sh
~/.termux/boot/start-minecraft
```

If Paper is already running, the script should exit without launching another copy. Inspect the process list and `~/minecraft-server/logs/console.log` to confirm the result.

## Verified on the target phone

- The user confirmed Termux:Boot was installed from F-Droid and opened once.
- `termux-wake-lock` is available in Termux tools.
- `~/.termux/boot/start-minecraft` is executable with mode `700` and passes `sh -n`.
- Running the script manually while Paper and `sshd` were active left one Paper process and one SSH daemon process.
- The running Paper process remains separate from the SSH command; the server reached `Done` after the detached launch.
- The phone has not yet been rebooted to test the actual Termux:Boot event.

## Android power and heat settings

These are still manual checks on the phone:

1. In Android app settings, set Termux and Termux:Boot battery use to unrestricted or allow background activity. OPPO/ColorOS may also have a vendor-specific background-power or auto-launch control.
2. Keep Termux:Boot allowed to run at startup and avoid force-stopping Termux.
3. Use stable power and place the phone on a hard, ventilated surface. Do not cover it or run it in direct sun. Stop the server if the phone becomes unusually hot, swells, or shows battery damage.
4. Do not assume continuous charging is safe for a worn battery. Use a manufacturer-supported charge limit if the device provides one, and periodically inspect battery condition and temperature.
5. After these settings are confirmed, schedule a controlled reboot while local access is available. Check the SSH port, `java` process, server `Done` line, and Paper's TCP port before relying on unattended operation.

Termux's own guidance recommends disabling Android battery optimizations when background process termination occurs; the exact OPPO menu names vary by Android and ColorOS version. See the [Termux app installation guidance](https://github.com/termux/termux-app#installation).

The operator reports completing the battery/background setting for both Termux apps on the target phone. Android does not expose that setting through the Termux SSH session, so it has not been independently read back.

## Security

The boot script contains no credentials. It restores SSH access after boot, so protect the phone with a screen lock and keep SSH key authentication enabled. Never publish the phone's IP address, SSH private key, server logs, world, or live configuration. The server is not ready for unattended public access until the tunnel and private dashboard phases are separately configured and secured.
