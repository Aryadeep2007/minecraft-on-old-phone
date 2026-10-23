# Troubleshooting

Record observed errors and fixes here. When full verification is pending, the outcome column states that explicitly.

| Phase | Symptom | Cause | Verified workaround or outcome |
|---|---|---|---|
| Termux setup | A network-interface lookup reported a netlink socket permission error | Android restricted the interface query from Termux | Read the phone's local Wi-Fi address in Android Settings → Wi-Fi → connected network details |
| Termux setup | `ps -A -o PID,...` rejected the requested format | Android's bundled `ps` uses a different option set | `ps -A` worked to confirm whether the Java process was running |
| PaperMC | Paper logged JLine `libutil.so.1` and OSHI/JNA `libudev` native-library warnings | Optional native terminal and hardware probes could not load Linux libraries in the Termux environment | Paper continued through remapping and reached the EULA check; full startup still needs verification |
