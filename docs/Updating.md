<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Updating

[Home](Home.md) › Updating

**Contents:** [Change your channels](#change-your-channels) · [Change a setting](#change-a-setting) ·
[Update the server tool](#update-the-server-tool)

## Change your channels

The settings files are mounted read-only, so the tool's page cannot change them. Edit `channel_list.json` on the
Docker machine, then restart the container
(`docker compose -p chromatube restart`) and start a run from the tool's page (or wait for the next one). Then
`py -3 tools\chromatube_library.py refresh --yes --ask-admin`. A removed channel's folder can be deleted by hand from
the ChromaTube folder.

## Change a setting

Edit the `.json` file, then **restart the container** (`docker compose -p chromatube restart`): the tool's own
"restart service" button may not reload its settings. After changing `video_quality` or the hand-over settings, also
clear the tool's direct-stream cache (in its page, or `docker compose -p chromatube down -v` and `up -d`, which also
empties its data volume; your channel list and the `.strm` folder are kept).

## Update the server tool

YouTube changes things now and then; then videos stop starting until a newer image of ytdlp2STRM (with a newer
yt-dlp) is out. The image is **pinned by digest**, so it never changes by itself.

**What the pin is:** `sha256:2757a5e7293d7e885d5dc057b26a9e8cb9b5a5b2a6affe6a3e9f7f8c5fb9ec7c`, the build the publisher
tagged `latest` on 2026-10-25 (upstream commit 7d4a047). It is **not** a release tag: the newest release tags point at
older builds with other digests. If the publisher ever prunes untagged images, this digest may stop being pullable;
then choose a newer one as below. Keep a note of the digest you run, so you can go back.

To move to a newer build on purpose:

1. Look at what changed: [github.com/fe80Grau/ytdlp2STRM](https://github.com/fe80Grau/ytdlp2STRM) (commits and
   releases).
2. On the Docker machine, pull the build you chose (a release tag, or `latest` at that moment) and read its digest:
   `docker pull fe80grau/ytdlp2strm:latest`, then
   `docker image inspect --format "{{index .RepoDigests 0}}" fe80grau/ytdlp2strm:latest`.
3. Put that `fe80grau/ytdlp2strm@sha256:...` into `docker-compose.yml` in place of the old one (never the tag itself)
   and run `docker compose -p chromatube up -d`.
4. Check that the page still asks for its sign-in, then `py -3 tools\chromatube_library.py test` should PASS again. If
   not, put the old digest back.

Never use a moving tag such as `latest`, and never add an automatic updater: an update is a new program on your
server and deserves a look first.

Next: [Security](Security.md)
