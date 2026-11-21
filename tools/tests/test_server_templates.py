# SPDX-License-Identifier: GPL-3.0-or-later
# Additional terms: ADDITIONAL-TERMS.md
"""The server templates in server/ keep their safety settings (standard library only, no Docker needed).

- the image is pinned by a sha256 digest, never a moving tag;
- the tool's page sign-in is required: the example config cannot be used as it is, config.json is never in the
  repository and is Git-ignored, and make_server_config.py writes a random user name and password, outside the
  repository only;
- the four settings files are mounted read-only; no untested capability changes (cap_drop/cap_add);
- Security.md says the sign-in does not cover the tool's command channel (the firewall is the real protection);
- no YouTube cookies, no Jellyfin API key, the tool's own Jellyfin link off;
- 360p sources (a light conversion on the server) and the address hand-over that gives Jellyfin sound;
- resource limits, no privilege escalation, rotated logs;
- no catch-all listening address, no personal paths, no real channels in the example;
- the four settings files are valid JSON.

    py -3 tools/tests/test_server_templates.py
"""
import io
import json
import re
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2] / 'server'
failures = []


def check(ok, what):
    print(('ok   ' if ok else 'FAIL ') + what)
    if not ok:
        failures.append(what)


def test_make_server_config():
    sys.path.insert(0, str(SERVER.parent / 'tools'))
    import make_server_config as tool
    with tempfile.TemporaryDirectory() as folder:
        out = Path(folder) / 'chromatube'
        written = tool.make('192.168.1.20', out)
        on_disk = json.loads((out / 'config.json').read_text(encoding='utf-8'))
        check(on_disk == written and len(on_disk['ytdlp2strm_web_password']) >= 24
              and on_disk['ytdlp2strm_web_username'].startswith('chromatube-') and on_disk['ytdlp2strm_host'] == '192.168.1.20',
              'make_server_config.py writes a random page sign-in and the LAN address')
        check(all((out / name).is_file() for name in ('docker-compose.yml', '.env.example', 'crons.json', 'yt_config.json',
                                                     'channel_list.json')), 'it copies the other server files')
        other = tool.make('192.168.1.20', Path(folder) / 'second')
        check(other['ytdlp2strm_web_password'] != written['ytdlp2strm_web_password'], 'every copy gets its own password')
        for host in ('0.0.0.0', '8.8.8.8', '127.0.0.1', 'evil.example.com'):
            try:
                tool.make(host, Path(folder) / ('h' + host.replace('.', '-')))
                refused = False
            except ValueError:
                refused = True
            check(refused, f'it refuses the address {host} (not a LAN address)')
        for target in (SERVER.parent / 'server-copy', out):
            try:
                tool.make('192.168.1.20', target)
                refused = False
            except ValueError:
                refused = True
            check(refused and not (SERVER.parent / 'server-copy').exists(),
                  'it refuses a folder inside the repository' if target != out else 'it never overwrites a config.json')
        out_text = io.StringIO()
        with redirect_stdout(out_text):
            tool.main(['--host', '192.168.1.21', '--out', str(Path(folder) / 'third')])
        secret = json.loads((Path(folder) / 'third' / 'config.json').read_text(encoding='utf-8'))['ytdlp2strm_web_password']
        check(secret not in out_text.getvalue(), 'the password is never printed')


def main():
    full = (SERVER / 'docker-compose.yml').read_text(encoding='utf-8')
    compose = '\n'.join(line.split('#', 1)[0] for line in full.splitlines())   # the settings, without comments
    images = re.findall(r'^\s*image:\s*(\S+)', compose, re.M)
    check(len(images) == 1 and re.fullmatch(r'[\w./-]+@sha256:[0-9a-f]{64}', images[0]) is not None,
          'the image is pinned by digest')
    check(':latest' not in compose and 'watchtower' not in compose.lower(), 'no moving tag, no automatic updater')
    check('mem_limit:' in compose and 'cpus:' in compose and 'pids_limit:' in compose, 'memory, CPU and process limits')
    check('no-new-privileges:true' in compose and 'max-size' in compose, 'no privilege escalation; logs rotated')
    check('cap_drop' not in compose and 'cap_add' not in compose,
          'no untested capability changes (dropping them can stop the tool reading its settings)')
    security = (SERVER.parent / 'docs' / 'Security.md').read_text(encoding='utf-8')
    check('command channel' in security and 'Socket.IO' in security and 'real protection' in security,
          'Security.md says the sign-in does not cover the command channel and the firewall is the real protection')
    check('0.0.0.0' not in compose and 'privileged: true' not in compose and 'docker.sock' not in compose
          and 'ports:' not in compose, 'no catch-all address, no published ports, no privileged mode, no Docker socket')
    check(':?set CHROMATUBE_LIST_FOLDER' in compose, 'the list folder must be set on purpose (.env)')
    volumes = compose.split('volumes:', 1)[1].split('restart:', 1)[0]
    mounts = [line.strip()[2:] for line in volumes.splitlines() if line.strip().startswith('- ')]
    targets = [re.search(r':(/(?:media|opt)/[^:\s]*)(:ro)?$', m) for m in mounts]
    check(len(mounts) == 6 and all(targets), 'only the list folder, its own data and its four settings files are mounted')
    settings_mounts = [x for x in targets if x and x.group(1).endswith('.json')]
    check(len(settings_mounts) == 4 and all(x.group(2) == ':ro' for x in settings_mounts),
          'the four settings files are mounted read-only (the page cannot change them)')

    settings = {name: json.loads((SERVER / name).read_text(encoding='utf-8'))
                for name in ('config.example.json', 'yt_config.json', 'crons.json', 'channel_list.example.json')}
    check(True, 'the four settings files are valid JSON')
    yt = settings['yt_config.json']
    check(yt['cookie_value'] == '' and yt['cookies'] != 'cookies-from-browser', 'no YouTube cookies (no account used)')
    check(yt['jellyfin_integration'] == 'False' and yt['jellyfin_api_key'] == '' and yt['jellyfin_base_url'] == '',
          'the tool has no Jellyfin key and no Jellyfin link')
    check(yt['video_quality'] == '360' and yt['direct_serve_media_playlist'] == 'False',
          '360p sources, handed over in the form that gives Jellyfin sound')
    check(yt['strm_output_folder'] == '/media/ChromaTube' and int(yt['videos_limit']) <= 15, 'one folder, at most 15 videos a channel')
    config = settings['config.example.json']
    check(config['ytdlp2strm_host'].startswith('CHANGE-ME') and config['ytdlp2strm_port'] == '5005',
          'the listening address is left for you to set (your LAN address)')
    check(config['ytdlp2strm_web_username'].startswith('CHANGE-ME') and config['ytdlp2strm_web_password'].startswith('CHANGE-ME'),
          'the example shows the page sign-in as required (never empty, never a usable default)')
    check(not (SERVER / 'config.json').exists(), 'no config.json (with a sign-in) is shipped in the repository')
    ignored = (SERVER.parent / '.gitignore').read_text(encoding='utf-8').splitlines()
    check('server/config.json' in ignored and 'config.json' in ignored, 'config.json is Git-ignored')
    test_make_server_config()
    check(settings['crons.json'][0]['qty'] == '6' and 'direct' in settings['crons.json'][0]['do'], 'lists refreshed every 6 hours, on demand mode')
    check(all('ReplaceWith' in url for url in settings['channel_list.example.json']), 'the example names no real channel')

    text = '\n'.join(p.read_text(encoding='utf-8') for p in SERVER.iterdir() if p.is_file()).replace('0.0.0.0', '')
    check(not re.search(r'/volume\d|[A-Z]:\\|\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', text), 'no personal paths or addresses')
    print('PASS' if not failures else f'FAIL: {len(failures)} check(s) failed')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
