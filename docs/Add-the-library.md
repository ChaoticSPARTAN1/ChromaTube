<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Add the library

[Home](Home.md) › Add the library

**Contents:** [Get the tools](#get-the-tools) · [1. Check](#1-check) · [2. Add (dry run, then for real)](#2-add-dry-run-then-for-real) ·
[3. Refresh](#3-refresh) · [4. Test](#4-test) · [5. Let the console see it](#5-let-the-console-see-it)

The console's ChromaTube row looks for **one library named exactly "ChromaTube"**. `tools/chromatube_library.py`
adds it safely: add-only, with a backup, a dry run and proof that nothing else changed
([Security](Security.md)).

## Get the tools

Install **Python 3.10+**, download this repository and open a terminal in its folder (`py -3` on Windows,
`python3` elsewhere). `--ask-admin` asks for an administrator's name and password for that one run, keeps them in
memory only and signs that run's own session out at the end; nothing is saved and no other device is signed out.

## 1. Check

```
py -3 tools\chromatube_library.py check --server-path /config/ChromaTube --ask-admin
```

Read-only. It checks the server version, that the server **sees** the folder (and how many channel folders are in
it), that the folder is **outside every existing library folder**, and that no library is called ChromaTube yet.

## 2. Add (dry run, then for real)

```
py -3 tools\chromatube_library.py add --server-path /config/ChromaTube --ask-admin
py -3 tools\chromatube_library.py add --server-path /config/ChromaTube --yes --ask-admin
```

The first only shows what it would do. The second saves a backup of the library list and a fingerprint of users,
devices, plugins, tasks and conversion settings, then adds **one** library:

| Setting | Value |
|---|---|
| Name | ChromaTube |
| Type | Shows (channels as shows, years as seasons) |
| Folder | the one you gave |
| Real-time monitoring, internet metadata, chapter pictures, trickplay pictures | off |
| Scan | none server-wide: the next step scans only this library |

Then it proves every other library is byte for byte unchanged and records the library's name, id and folder in your
private folder (`%LOCALAPPDATA%\ChromaTube`), so `remove` can later delete exactly it.

## 3. Refresh

```
py -3 tools\chromatube_library.py refresh --yes --ask-admin
```

Scans **only** the ChromaTube library and reports how many channels it holds. Afterwards Jellyfin's own scheduled
library scan picks up new videos; run `refresh` again whenever you do not want to wait.

## 4. Test

```
py -3 tools\chromatube_library.py test
```

Plays the newest video for 12 seconds exactly the way the console does (it asks Jellyfin's PlaybackInfo first, then
the small MJPEG + ADPCM stream), reports the first-picture time and format as numbers, and stops its own conversion.
`PASS a ChromaTube video plays through Jellyfin in the Chromatic format` means the console will play it too.

## 5. Let the console see it

The console plays as its own Jellyfin user. If that user has access to only some libraries, add ChromaTube:
**Dashboard › Users › the console's user › Library access**. Then: start-up menu › **ChromaTube**
([Using ChromaTube](Using-ChromaTube.md)).

**Switch the row on:** ChromaTube is off on a new console. Chromatic Manager › **Settings › Apps** › ChromaTube on,
**Save and write to console**, **Approve** (or, if you hid it on the console: Other firmware › Show hidden apps).

**With Chromatic Manager instead of this tool:** **Settings › ChromaTube server** › **Find it**, **Dry run**, **Add
library**. Both add the same library with the same options and record it with the same keys, so either one's remove
works on it.

Next: [Using ChromaTube](Using-ChromaTube.md)
