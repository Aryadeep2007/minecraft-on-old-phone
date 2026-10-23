# Security

## Secrets and repository hygiene

- Never commit passwords, RCON credentials, SSH keys, tunnel tokens, real phone IP addresses, world data, player data, server jars, or logs.
- Keep real configuration on the phone. Publish only sanitized files whose names end in `.example`.
- Before each push, inspect staged file names and diffs for secrets and private information.

## Network access

- Never expose the RCON port or dashboard directly to the public internet.
- Bind RCON to localhost and use a private access network for the dashboard.
- Forward only the game ports required by the chosen tunnel: Java uses TCP and Bedrock uses UDP.

## Authentication

Offline mode disables Mojang account verification at the server. Names can be impersonated unless a trusted login plugin and whitelist are configured and working. Use unique passwords and understand plugin compatibility before inviting players.

## Operations

Keep the phone cool, avoid unsafe charging or battery modifications, and maintain backups. Test restoration before relying on backups.
