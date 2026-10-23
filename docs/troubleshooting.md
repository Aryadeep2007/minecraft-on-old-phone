# Troubleshooting

Record observed errors and fixes here. When full verification is pending, the outcome column states that explicitly.

| Phase | Symptom | Cause | Verified workaround or outcome |
|---|---|---|---|
| Termux setup | A network-interface lookup reported a netlink socket permission error | Android restricted the interface query from Termux | Read the phone's local Wi-Fi address in Android Settings → Wi-Fi → connected network details |
| Termux setup | `ps -A -o PID,...` rejected the requested format | Android's bundled `ps` uses a different option set | `ps -A` worked to confirm whether the Java process was running |
| PaperMC | Paper logged JLine `libutil.so.1` and OSHI/JNA `libudev` native-library warnings | Optional native terminal and hardware probes could not load Linux libraries in the Termux environment | Paper reached `Done` and shut down cleanly; no workaround was needed for this startup |
| PaperMC | Netty could not find a hardware MAC address; Spark async-profiler could not load `libdl.so.2` | Android/Termux does not expose these Linux native libraries/interfaces in the expected form | Paper generated a random MAC fallback, reached `Done`, and shut down cleanly; Spark's optional async profiler remains unavailable |
| PaperMC | Paper printed command-line help and rejected an option on the first start-script launch | A Windows CRLF line ending added a carriage return to the final Java argument | Run `sed -i 's/\r$//' ~/minecraft-server/start.sh` on Termux; the LF-normalized script then reached `Done` and shut down cleanly |
| Bedrock connectivity | Floodgate warned that `en_` is not a supported language during startup | The phone's environment selected a locale identifier that Floodgate does not recognize | Floodgate still completed startup and Geyser started; player behavior has not been tested |
| Bedrock connectivity | NetherNet initialization failed with `Cannot identify the JVM's libc` after selecting `transport: both` | Geyser's current native library bundles glibc and musl builds, while Termux uses Android/Bionic | Restored `transport: raknet` and `webrtc-port: 0`; Geyser starts its UDP listener, but NetherNet remains unavailable in this Termux runtime |
