<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Troubleshooting

[Home](Home.md) › Troubleshooting

**Contents:** [On the console](#on-the-console) · [The server tool](#the-server-tool) · [The library tool](#the-library-tool)

## On the console

| Problem | Try |
|---|---|
| **ChromaTube isn't set up on your server** | Add the library ([Add the library](Add-the-library.md)); give the console's user access to it |
| The row is missing from the start-up menu | ChromaTube is off on a new console: Chromatic Manager › Settings › Apps; if you hid it: Other firmware › Show hidden apps; or the start-up menu is older than 1.6 |
| No channels in the library | The tool has not run yet, or the library was not refreshed: `refresh --yes` |
| A video does not start | `py -3 tools\chromatube_library.py test`; if it fails, see the server tool below |
| Picture full size, no sound | You opened it from the **Jellyfin** row: open ChromaTube videos from the **ChromaTube** row |
| No sound in any video | Sound needs Jellymatic's console chip image 18.40 or 18.41 |
| It stops after a while | Wi-Fi dropped or the server is busy; videos always start again from the beginning |

## The server tool

| Problem | Try |
|---|---|
| Its page asks for a user name and password | That is the required sign-in: the values are in `config.json` on the Docker machine (or in your copy) |
| A change made in its page does not stick | The settings files are read-only on purpose: edit them on the Docker machine, then `docker compose -p chromatube restart` |
| The container does not start | `docker logs chromatube-ytdlp2strm`; check that `config.json`, `channel_list.json` and `.env` exist next to `docker-compose.yml` (a missing file makes Docker create an empty folder in its place); if the log says it cannot read `config.json`, check that file's owner and permissions on the Docker machine |
| Its page does not open | `ytdlp2strm_host` must be the Docker machine's LAN address and the compose file must use host networking; check the firewall rule for 5005 (from your PC it opens only while the temporary rule for your PC is in place) |
| The ChromaTube folder stays empty | Start a run from its page; check `channel_list.json` (valid JSON, real channel addresses); look at its log on the page |
| Videos list, but none plays | YouTube may have changed something: [update the tool](Updating.md#update-the-server-tool). After a settings change, restart the container (its own restart button may not reload settings) |
| Videos play without sound, or huge | Keep `video_quality` "360" and `direct_serve_media_playlist` "False", restart the container and clear its direct-stream cache ([Updating](Updating.md#change-a-setting)) |
| An age-restricted video never plays | Expected: they need cookies, and ChromaTube never uses cookies |

## The library tool

| Message | Means |
|---|---|
| `the server cannot see the folder` | The path is the one your PC or Docker machine sees, not Jellyfin's; or the folder is not mounted into the Jellyfin container |
| `the folder is inside (or contains) an existing library folder` | Choose a folder of its own, outside every library |
| `a library named ChromaTube already exists` | Remove it first (by hand if it was not made by this tool) |
| `the ChromaTube library on the server is not the one recorded` | It was changed or re-made by hand since; `remove` will not touch it. Remove it by hand if you want it gone |
| `FAIL no saved Jellyfin settings found` | Use `--ask-admin` |

Next: [FAQ](FAQ.md)
