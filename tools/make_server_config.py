# SPDX-License-Identifier: GPL-3.0-or-later
# Additional terms: ADDITIONAL-TERMS.md
"""Make your own copy of ChromaTube's server files, OUTSIDE this repository, with the tool's page sign-in set.

    py -3 tools/make_server_config.py --host 192.168.1.20 --out D:\\chromatube

It copies server/ (docker-compose.yml, .env.example, crons.json, yt_config.json, channel_list.example.json) into
--out and writes config.json there with:
  - ytdlp2strm_host: the address you give (this machine's LAN address: a private IPv4 address or a local name;
    never 0.0.0.0, never a public address);
  - ytdlp2strm_web_username / ytdlp2strm_web_password: a random user name and a long random password. The sign-in is
    REQUIRED: without it anyone on your network who can reach port 5005 could change the tool's settings. It guards
    only the settings pages: the tool's command channel has no sign-in and can start programs inside its container,
    so the firewall rule is the real protection (port 5005 only from your Jellyfin server; your PC only while you
    check it).
It also copies channel_list.example.json to channel_list.json when there is none yet. The new files are readable by you
only on macOS/Linux (if the tool cannot read its settings, check the file's owner and permissions). Nothing is printed of the sign-in: open config.json to read it. Never commit or share config.json.
It refuses to write inside this repository (so the sign-in cannot end up in Git) and never overwrites a config.json.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import secrets
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jellyfin_admin as ja  # noqa: E402  (private folder and file helpers)

REPO = Path(__file__).resolve().parents[1]
SERVER = REPO / 'server'
COPIED = ('docker-compose.yml', '.env.example', 'crons.json', 'yt_config.json', 'channel_list.example.json')


def lan_host(text: str) -> bool:
    """A private IPv4 address (10/8, 172.16/12, 192.168/16) or a plain local host name; never 0.0.0.0 or public."""
    try:
        address = ipaddress.ip_address(text)
        return address.version == 4 and address.is_private and not address.is_loopback and not address.is_unspecified \
            and not address.is_link_local
    except ValueError:
        return bool(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,62})(?:\.(?:local|lan|home|internal|home\.arpa))?', text))


def make(host: str, out: Path):
    """Returns the written config (for the tests)."""
    if not lan_host(host):
        raise ValueError('--host must be this machine\'s LAN address (for example 192.168.1.20) or a local name')
    if ja.inside(out, REPO):
        raise ValueError('choose a folder outside the repository: config.json holds the page sign-in')
    if (out / 'config.json').exists():
        raise ValueError('config.json already exists there; nothing was changed')
    ja.private_dir(out)
    for name in COPIED:
        shutil.copyfile(SERVER / name, out / name)
    if not (out / 'channel_list.json').exists():
        shutil.copyfile(SERVER / 'channel_list.example.json', out / 'channel_list.json')
    config = json.loads((SERVER / 'config.example.json').read_text(encoding='utf-8'))
    config['ytdlp2strm_host'] = host
    config['ytdlp2strm_web_username'] = 'chromatube-' + secrets.token_hex(4)
    config['ytdlp2strm_web_password'] = secrets.token_urlsafe(24)
    ja.save_private(out / 'config.json', config)
    return config


def main(argv=None):
    parser = argparse.ArgumentParser(description='Your own copy of the ChromaTube server files, with the page sign-in set.')
    parser.add_argument('--host', required=True, help="this machine's LAN address, the one Jellyfin uses to reach it")
    parser.add_argument('--out', required=True, help='a new folder outside this repository')
    args = parser.parse_args(argv)
    try:
        make(args.host, Path(args.out))
    except (ValueError, OSError) as error:
        print(f'FAIL {error}' if isinstance(error, ValueError) else 'FAIL the files could not be written; nothing usable was made')
        return 2 if isinstance(error, ValueError) else 1
    print('PASS server files written, with config.json holding a random page sign-in (open it to read the user name '
          'and password; never commit or share it)')
    print('INFO next: set the folder in .env (copy .env.example), your channels in channel_list.json, the firewall rule '
          'for port 5005 (from your Jellyfin server only; it is the real protection, the sign-in guards only the '
          'settings pages), then start it (docs/Server-setup.md)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
