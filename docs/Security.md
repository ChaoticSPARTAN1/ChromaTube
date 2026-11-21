<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Security

[Home](Home.md) › Security

**Contents:** [Keep it on your home network](#keep-it-on-your-home-network) · [The container](#the-container) ·
[The tool's own page](#the-tools-own-page) · [Sign-ins](#sign-ins) · [The library tool's rules](#the-library-tools-rules) ·
[Checklist](#checklist)

## Keep it on your home network

- **Jellyfin stays off the internet** for ChromaTube: no port forward, no public reverse proxy. The console, the
  container and the PC tools need it on your home network only.
- **The container's port 5005 stays off the internet** too: no port forward on your router. On the Docker machine's
  firewall allow 5005 **only from your Jellyfin server (required)**; allow your PC only while you run **Check it
  answers** or open the tool's page, then remove that rule. This firewall rule is the real protection
  ([what the sign-in does not cover](#what-the-sign-in-does-not-cover)).
- The container listens only on the LAN address you put in `config.json` (never `0.0.0.0`). Its video addresses
  (`/youtube/...`) need no sign-in, because Jellyfin must reach them; that is why it must not be reachable from
  outside.

## The container

| Setting | Why |
|---|---|
| Image pinned by **sha256 digest** | It cannot change by itself; updates are your choice ([Updating](Updating.md)) |
| `mem_limit: 1g`, `cpus: 1.5`, `pids_limit: 256` | It cannot take over the machine |
| `no-new-privileges` | No privilege escalation inside the container |
| Mounts: the one ChromaTube folder, its own data volume, its four settings files **read-only** | **Nothing of Jellyfin's** (no configuration, no database, no media drives), no Docker socket; the tool cannot change its own settings or sign-in (edit the files on the Docker machine, then restart the container) |
| The page sign-in, **required** | See below |
| **No cookies, no YouTube account, no API key** (`cookie_value` empty) | Nothing of yours to leak; age-restricted videos simply do not play. Never add cookies: they would tie your Google account to an unofficial tool |
| No Jellyfin key, Jellyfin link off (`jellyfin_integration` False) | The container cannot change your Jellyfin server at all; the library is refreshed by Jellyfin's own schedule or by `refresh` from your PC |
| 360p sources | A light conversion on your server |
| Logs rotated (3 × 10 MB) | They cannot fill the disk |

`tools/tests/test_server_templates.py` checks these settings in the templates.

**Dropping Linux capabilities** (`cap_drop: [ALL]`) is optional extra hardening that was **not tested** with this
image: without them the tool may be unable to read its settings or write its folder, so the template does not use it.
Add it yourself only if you test it on your own machine.

**If the tool cannot read its settings** (its log shows an error reading `config.json`, or it stops right after
starting), check the file's owner and permissions on the Docker machine: `make_server_config.py` writes `config.json`
readable by you only on macOS/Linux, which the container (running as root, with its normal capabilities) can still
read.

## The tool's own page

The page on port 5005 can change the tool's settings. Without a sign-in, its settings pages are open to anyone who can
reach the port. So the sign-in is **required**: `ytdlp2strm_web_username` and
`ytdlp2strm_web_password` in `config.json` must both be set. Chromatic Manager's **Save files** and
`tools/make_server_config.py` each write a random user name and a long random password for you (the Manager keeps a
private copy on your PC, never shows it, and its **Check it answers** passes only when the page refuses a visitor without
the sign-in and answers with it) ([Server set-up](Server-setup.md#2-make-your-copy-of-the-files)); by hand, make up a long
password you use nowhere else.

- The video addresses Jellyfin uses (`/youtube/...`) stay open, as they must: that is why the firewall rule is
  required too.
- The password is stored in `config.json` on the Docker machine (and in your copy): keep the file private, never commit
  or share it. The repository ships only `config.example.json`, and `.gitignore` keeps `config.json` out of Git.
- With the settings mounted read-only, the page cannot change the sign-in or your channels.

### What the sign-in does not cover

In the pinned version the sign-in protects the settings pages only. The tool's live command channel (Socket.IO, used
by its page to run its own command line) has no sign-in and accepts connections from any web page, and it can start
programs inside the container. So anything that can reach port 5005, including a web page open in a browser on an
allowed computer, could use it. **The firewall rule is the real protection:** allow 5005 from your Jellyfin server
only; allow your PC only while you run **Check it answers** or open the page, then remove that rule.

## Sign-ins

- **The console** keeps its own normal (non-administrator) Jellyfin sign-in, made with Quick Connect.
- **The administrator** is used only on the PC, only to add, refresh or remove the library: `--ask-admin` keeps the
  name and password in memory for that one run, signs in as a device made for that run, and signs that one session out
  at the end. Nothing is saved.
- **No other session or device is ever signed out.**

## The library tool's rules

Every request that could change the server is checked against a short allow-list before it is sent; anything else is
refused unsent:

| Command | Changing requests it may send |
|---|---|
| `check`, `status` | none |
| `add --yes` | `POST /Library/VirtualFolders?name=ChromaTube` (no server-wide scan) |
| `refresh --yes` | `POST /Items/{the ChromaTube library}/Refresh` |
| `test` | open one ChromaTube video (PlaybackInfo), stop its own conversion, close it |
| `remove --yes` | `DELETE /Library/VirtualFolders?name=ChromaTube`, only when the name, id and folder match the record |
| any, with `--ask-admin` | its own sign-in, and the sign-out of that one session |

It prints counts and PASS/FAIL lines, never an address, path, name, token or id. Its tests run every command against a
fake server that holds other libraries, users and sessions.

## Checklist

- [ ] Jellyfin and port 5005 are not forwarded on the router
- [ ] Firewall: 5005 only from the Jellyfin server (required); the PC only temporarily, while you check it
- [ ] `config.json`: your LAN address; page user name and password set (required), the file kept private
- [ ] `yt_config.json`: `cookie_value` empty, `jellyfin_api_key` empty
- [ ] `docker-compose.yml`: an `@sha256:` digest, `no-new-privileges`, `:ro` settings mounts, unchanged limits
- [ ] The console signs in as a normal user

Next: [Undo everything](Undo-everything.md)
