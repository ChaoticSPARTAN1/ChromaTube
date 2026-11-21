<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Building and testing

[Home](Home.md) › Building and testing

**Contents:** [Where the code is](#where-the-code-is) · [Tests](#tests) · [Documentation](#documentation) ·
[Rules for changes](#rules-for-changes)

## Where the code is

| What | Where |
|---|---|
| The server set-up | `server/` here: the Docker Compose file and the tool's settings templates (`config.example.json`, never a filled-in `config.json`); `tools/make_server_config.py` makes your own copy with a random page sign-in |
| The library tool | `tools/chromatube_library.py` here, with `jellyfin_admin.py`, the small careful Jellyfin client it shares with Chromavision's tools |
| The ChromaTube row on the console (library browser, PlaybackInfo-first playback) | Jellymatic: `chromatic/jellyfin/` (the Jellyfin app in its ChromaTube mode) and `chromatic/launcher/` |
| The Apps switches | Jellymatic: Chromatic Manager and the start-up menu |
| The row's icon | `art/chromatube-icon-12.png` here: a stack of three violet video cards, the same pixels as the console's (drawn by Jellymatic's `scripts/build_app_icons.py`) |
| ytdlp2STRM and yt-dlp | Not here: Docker downloads the pinned image ([fe80Grau/ytdlp2STRM](https://github.com/fe80Grau/ytdlp2STRM)) |

## Tests

Standard library only; no Docker, no device, no internet (the fake Jellyfin server listens on 127.0.0.1):

```
py -3 tools\tests\test_chromatube_library.py
py -3 tools\tests\test_server_templates.py
py -3 tools\tests\test_private_files.py
py -3 scripts\test_docs_html.py
```

`test_chromatube_library.py` runs every command against a fake server that already holds other libraries, users and
sessions, with failures injected (add refused, delete fails, no videos, a library replaced by hand, a folder inside
another library, a folder the server cannot see). It checks that only allow-listed requests are sent, every other
library stays byte for byte the same, nothing private is printed and only the run's own session is signed out.
`test_server_templates.py` checks the safety settings of the files in `server/` (pinned digest, required sign-in,
read-only settings, no privilege escalation, no cookies or keys; Security.md still explains what the sign-in does not cover) and `make_server_config.py` (random sign-in, LAN addresses
only, never inside the repository, never printed). `test_private_files.py` checks that backups are user-only on
macOS/Linux.

## Documentation

After editing any page: `py -3 scripts\build_docs_html.py`, then `py -3 scripts\build_docs_pdf.py` (needs Chrome or
Edge), then `py -3 scripts\test_docs_html.py`. GitHub Pages: Settings › Pages, branch `main`, folder `/docs`.

## Rules for changes

- Keep the rules of [Security](Security.md): add-only, backup, dry run, proof, allow-listed requests, nothing private
  printed, never sign out another session; a pinned digest; no cookies, keys or accounts in templates.
- Never add channel lists, videos or anything personal.
- Plain words in anything a user reads.

Next: [Credits & licences](Credits-and-licences.md)
