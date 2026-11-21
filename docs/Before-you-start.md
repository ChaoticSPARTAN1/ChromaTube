<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Before you start

[Home](Home.md) › Before you start

**Contents:** [YouTube's terms](#youtubes-terms) · [How it works](#how-it-works) · [What it costs your server](#what-it-costs-your-server) ·
[Who can see what](#who-can-see-what) · [What it does not do](#what-it-does-not-do)

## YouTube's terms

ChromaTube's server side uses **ytdlp2STRM**, which uses **yt-dlp** to find each video's address and hand it to your
Jellyfin server. **This conflicts with YouTube's Terms of Service**: it reaches videos outside YouTube's own apps and
embedded player. The Chromatic cannot show YouTube's official player (it has no web browser and a 160 × 144 screen),
so there is no permitted way to watch YouTube on it.

Setting ChromaTube up is therefore **your own choice, for private viewing at home**, with the channels you choose.
ChromaTube itself contains no YouTube code and no video; it gives you a configuration for a third-party tool and
the safe Jellyfin set-up around it. YouTube Premium does not change this. In practice YouTube breaks such tools from
time to time; then videos stop starting until a newer image of the tool is out ([Updating](Updating.md)).

ChromaTube does not and **must not** be used to get around paid, members-only, rented or DRM-protected videos: it is
made for public videos only, and it uses no account and no cookies, so such videos do not play.

If you are not comfortable with this, **do not install it**: Games, Jellyfin and TV work without it, and the
ChromaTube row stays off.

## How it works

1. You list channels in `channel_list.json` on the Docker machine.
2. Every 6 hours the ytdlp2STRM container lists the newest videos of each channel (at most 15, from the last 30
   days) as tiny `.strm` files, one folder per channel, in the ChromaTube folder. **Nothing is downloaded.**
3. Jellyfin shows that folder as the library "ChromaTube" (channels as shows, years as seasons).
4. When you press Play on the console, Jellyfin asks the container for that one video (a 360p source), converts it
   into the console's small MJPEG picture and ADPCM sound, and streams it over your Wi-Fi.

## What it costs your server

- **Disk:** a few KB per video listed.
- **CPU:** one software conversion while you watch, from a 360p source (light), like a film in Jellyfin.
- **Network:** each played video is streamed from the internet to your server once, while it plays.
- **Memory and CPU of the container** are capped (1 GB, 1.5 CPU); it is idle between list updates.

## Who can see what

- **The library shows in your other Jellyfin apps too** (TV, phone), for every user allowed to see it, like any
  library. Hide it from a user in Dashboard › Users › that user › Library access (your choice; the tools never change
  users).
- **Google/YouTube sees** your home internet address fetching channel lists and the videos you play, with no account
  and no cookies.
- **Jellyfin keeps** resume points and watched marks for ChromaTube videos, as for any item.
- The tools print counts only; your channel list stays on your Docker machine.

## What it does not do

- No sign-in to YouTube or Google, no cookies, no API key, no comments, likes or subscriptions.
- No search of all of YouTube: only the channels you list.
- No downloads, no copies kept, no age-restricted videos (they need cookies: never add any).
- No seeking or resume on the console (one stream from the start; see [Using ChromaTube](Using-ChromaTube.md)).

Next: [Server set-up](Server-setup.md)
