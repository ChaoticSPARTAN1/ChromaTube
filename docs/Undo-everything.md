<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Undo everything

[Home](Home.md) › Undo everything

**Contents:** [The library](#the-library) · [The server tool](#the-server-tool) · [On the PC](#on-the-pc) · [On the console](#on-the-console)

## The library

```
py -3 tools\chromatube_library.py remove --ask-admin
py -3 tools\chromatube_library.py remove --yes --ask-admin
```

The first is a dry run. The second checks that the library on the server is still the one it recorded (name, id and
folder), removes only it, and proves every other library is unchanged. **Its files are not touched.**

**With Chromatic Manager:** Settings › ChromaTube server › **Remove library** (it also finds a library this tool added,
and this tool finds one the Manager added; a library added elsewhere is removed only when its folder is named ChromaTube
and holds channel folders, after you confirm it is yours). **By hand:** Jellyfin **Dashboard › Libraries › ChromaTube › Remove**. Nothing else was changed by ChromaTube.

What stays in Jellyfin afterwards: lines in its activity log, and watch history rows for the removed videos inside
its database (no longer shown anywhere once the items are gone).

## The server tool

On the Docker machine, in the `chromatube` folder:

```
docker compose -p chromatube down -v
```

It stops and deletes the container and its data volume (or, in a NAS Docker app: the project `chromatube` › Stop ›
Delete). Then delete the `chromatube` folder and the ChromaTube folder of `.strm` files. The Manager's private copy of the page
sign-in (`chromatube-server-signin.json` in its private folder) can be deleted too. Remove the firewall rule for
port 5005 if you added one. Optionally delete the image: `docker image rm fe80grau/ytdlp2strm@sha256:...`.

## On the PC

Delete `%LOCALAPPDATA%\ChromaTube` (on macOS/Linux `~/.local/share/chromatube`): the library record and backups. Then
delete the repository folder.

## On the console

Turn ChromaTube off in Chromatic Manager › **Settings › Apps**, or on the start-up menu highlight **ChromaTube**, press
**Select**, then **A** ("Hide ChromaTube?"): the row disappears from the start-up menu. With no library named ChromaTube the row would only say "ChromaTube is not set up on the
server". To remove Jellymatic's start-up menu altogether, see the
[Jellymatic recovery guide](https://github.com/ChaoticSPARTAN1/Jellymatic/blob/main/docs/Recovery.md).

Next: [Troubleshooting](Troubleshooting.md)
