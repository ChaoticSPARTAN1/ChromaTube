# Third-party notices

## Included in this repository

| Component | Files here | Licence | Licence text |
|---|---|---|---|
| Press Start 2P (CodeMan38) | `docs/fonts/heading-PressStart2P-Regular.ttf` | SIL OFL 1.1 | [LICENSES/OFL-1.1-PressStart2P.txt](LICENSES/OFL-1.1-PressStart2P.txt) |
| Silkscreen (The Silkscreen Project Authors) | `docs/fonts/body-Silkscreen-Regular.ttf` | SIL OFL 1.1 | [LICENSES/OFL-1.1-Silkscreen.txt](LICENSES/OFL-1.1-Silkscreen.txt) |

Everything else here is ChromaTube's own (GPL-3.0-or-later with [ADDITIONAL-TERMS.md](ADDITIONAL-TERMS.md)), including
the settings templates in `server/` (written for ChromaTube, in the format ytdlp2STRM reads).

## Referred to, not included

| Component | Licence | Where it comes from |
|---|---|---|
| ytdlp2STRM, Copyright (c) 2024 fe80grau | MIT ([its LICENSE](https://github.com/fe80Grau/ytdlp2STRM/blob/main/LICENSE)) | The Docker image `fe80grau/ytdlp2strm`, pinned by sha256 digest in `server/docker-compose.yml`; Docker downloads it from Docker Hub. Its image contains its own dependencies (yt-dlp, Python, Flask and others) under their own licences |
| yt-dlp | The Unlicense ([its LICENSE](https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE)) | Inside that image |
| Jellyfin server | GPL-2.0; the Jellyfin logo CC BY-SA 4.0 | Used through its public web API; no Jellyfin code or logo here |

**YouTube's terms.** ytdlp2STRM and yt-dlp reach videos outside YouTube's own apps and player, which conflicts with
YouTube's Terms of Service. ChromaTube contains neither; whether to run them is the user's choice
([docs/Before-you-start.md](docs/Before-you-start.md)). The videos belong to their creators.

## In Jellymatic's start-up menu (not included here)

The ChromaTube row is part of Jellymatic's start-up menu; its firmware components (ESP-IDF and others) and their
notices are listed in Jellymatic's THIRD-PARTY-NOTICES.md.
