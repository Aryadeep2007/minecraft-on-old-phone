# Troubleshooting

Only record errors and fixes that were actually observed and verified. No device-specific errors have been recorded yet.

| Phase | Symptom | Cause | Verified fix |
|---|---|---|---|
| Termux setup | A network-interface lookup reported a netlink socket permission error | Android restricted the interface query from Termux | Read the phone's local Wi-Fi address in Android Settings → Wi-Fi → connected network details |
