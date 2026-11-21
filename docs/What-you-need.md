<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# What you need

[Home](Home.md) › What you need

| You need | Why | Notes |
|---|---|---|
| A **ModRetro Chromatic** with Jellymatic's start-up menu **1.6.5 or newer**, signed in to your Jellyfin server | The ChromaTube row is part of it and uses the console's own Jellyfin sign-in | [Jellymatic guide](https://chaoticspartan1.github.io/Jellymatic/). Sound needs Jellymatic's console chip image 18.40 or 18.41. |
| A **Jellyfin server 10.9 or newer** on your **home network**, with video conversion working | It converts the video you play into the console's small format | Dashboard › Playback › Transcoding; keep it off the internet. |
| A machine on the same network that runs **Docker** (with Compose), with internet access | Runs the small ytdlp2STRM container | Often the NAS or server that runs Jellyfin. A NAS "Docker" or "Container" app works: paste the compose file as a project. |
| A **folder** that both the container and Jellyfin can see, **outside every existing library folder** | The container writes the video list there; Jellyfin reads it as the ChromaTube library | If Jellyfin runs in Docker, its configuration folder (seen as `/config`) is often the easiest place: `<config>/ChromaTube`. A brand-new mount into the Jellyfin container would need that container to be re-created (a restart): your decision. |
| An **administrator** name and password, **typed once on the PC** | Only an administrator may add a library | The tools ask with `--ask-admin`, keep it in memory for that run and sign that run out. |
| The console's **normal user** may see the ChromaTube library | The console plays as that user | Dashboard › Users › that user › Library access. |
| A **PC** with **Python 3.10 or newer** on the same network | Runs `tools/make_server_config.py` and `tools/chromatube_library.py` | Standard library only. |
| A **firewall** on the Docker machine you can set | Port 5005 must be reachable only from your Jellyfin server (and your PC only while you check it): the firewall is the real protection | Required: [Server set-up](Server-setup.md#4-close-port-5005-to-everyone-else). |

## Not needed

- **No YouTube or Google account, no cookies, no API key.**
- No Jellyfin plugin and no Jellyfin restart (if the folder is already visible to Jellyfin).
- No PC running while you watch.
- No disk space for videos: only tiny `.strm` files are written.

Next: [Before you start](Before-you-start.md)
