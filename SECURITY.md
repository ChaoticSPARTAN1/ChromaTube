<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Security

## Reporting a vulnerability

Please report security problems **privately**, not in a public issue: use GitHub's **Security › Report a
vulnerability** (private vulnerability reporting) on this repository. Describe the problem, how to reproduce it and
what it affects (the server templates, the library tool, the Jellyfin server, the console). There is no guarantee of a
response time; reports are handled as time allows. Problems in ytdlp2STRM itself belong to
[its project](https://github.com/fe80Grau/ytdlp2STRM); problems in the console code to
[Jellymatic](https://github.com/ChaoticSPARTAN1/Jellymatic).

## Never post publicly

- Jellyfin server addresses, user names, user IDs, tokens, device IDs
- Your Docker machine's address, `config.json` with a page password, `.env`
- Your channel list
- The files in your private folder (`%LOCALAPPDATA%\ChromaTube`)
- Logs or screenshots that show any of the above
- Never any cookies: ChromaTube does not use them, and nobody should ask you for them

## What ChromaTube does to protect you

- The server tool runs with a pinned image, memory/CPU/process limits, no privilege escalation, only its own folder
  mounted, no cookies, no account, no API key and no Jellyfin key; it listens only on your LAN address.
- The library tool prints counts and PASS/FAIL lines only, checks every changing request against a short
  allow-list, follows no redirects, and signs out only its own one-run session.
- An administrator sign-in is typed for one run (`--ask-admin`), kept in memory and never saved.
- Keep Jellyfin and port 5005 off the internet, and firewall 5005 to your Jellyfin server only (your PC only while you
  check it). The firewall is the real protection: in the pinned ytdlp2STRM the page sign-in guards only the settings
  pages, not its command channel ([docs/Security.md](docs/Security.md#what-the-sign-in-does-not-cover)).
