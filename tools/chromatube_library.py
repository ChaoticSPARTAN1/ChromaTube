# SPDX-License-Identifier: GPL-3.0-or-later
# Additional terms: ADDITIONAL-TERMS.md
"""Add, check, refresh, test and remove the ONE Jellyfin library ChromaTube plays from.

    py -3 tools/chromatube_library.py check --server-path PATH     read-only: is the server ready?
    py -3 tools/chromatube_library.py add --server-path PATH       dry run: shows exactly what would be added
    py -3 tools/chromatube_library.py add --server-path PATH --yes adds the library
    py -3 tools/chromatube_library.py refresh --yes                scans this one library for new videos
    py -3 tools/chromatube_library.py test                         plays one video the way the console does
    py -3 tools/chromatube_library.py status                       read-only
    py -3 tools/chromatube_library.py remove                       dry run
    py -3 tools/chromatube_library.py remove --yes                 removes exactly the library "add" recorded

--server-path is the folder the server tool (ytdlp2STRM) writes its .strm files into, as the JELLYFIN
SERVER sees it (for example /config/ChromaTube inside a Jellyfin container). It must already be visible
to Jellyfin and must not lie inside any existing library's folder (checked, read-only). The library is
named exactly "ChromaTube": the console's ChromaTube row looks for that name.

Sign-in: by default the saved Jellyfin settings (this tool's folder, then Jellymatic's). Adding and
removing a library needs an administrator: --ask-admin asks for an administrator's name and password for
this one run (memory only, never saved; that run's own session is signed out at the end). The console
keeps using its own, non-administrator sign-in.

Safety (docs/Security.md): add-only; the library list and a fingerprint of users, devices, plugins, task
triggers and conversion settings are saved first; the library is made with real-time monitoring,
internet metadata, chapter and trickplay pictures off, and no server-wide scan is started (refresh scans
this one library only); after the change the tool proves every other library is byte-for-byte unchanged;
remove checks the recorded name, id and folder still match and deletes only that library (its files are
not touched). Only these changing requests can ever be sent, everything else is refused unsent:
    POST   /Library/VirtualFolders?name=ChromaTube          (add)
    DELETE /Library/VirtualFolders?name=ChromaTube          (remove, only when the record matches)
    POST   /Items/{the ChromaTube library}/Refresh          (refresh)
    POST   /Items/{a ChromaTube video}/PlaybackInfo, POST /LiveStreams/Close,
    DELETE /Videos/ActiveEncodings                          (test: open, close and stop one video)
It prints PASS / FAIL / INFO lines and counts only: never an address, path, name, token or id.

Chromatic Manager (start-up menu 1.6.5 or newer, Settings > ChromaTube server) adds the same library with the same options and
records it with the same keys; this tool reads that record when it has none of its own, so either one's remove works.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jellyfin_admin as ja  # noqa: E402

APP = 'ChromaTube'
NAME = 'ChromaTube'          # the console looks for exactly this library name
OPTIONS = {'Enabled': True, 'EnableRealtimeMonitor': False, 'EnablePhotos': False, 'EnableInternetProviders': False,
           'SaveLocalMetadata': False, 'EnableChapterImageExtraction': False,
           'ExtractChapterImagesDuringLibraryScan': False, 'EnableTrickplayImageExtraction': False,
           'ExtractTrickplayImagesDuringLibraryScan': False, 'AutomaticRefreshIntervalDays': 0}


def state_dir():
    return ja.private_home(APP) / 'library'


def libraries(client):
    value, status = ja.read(client, '/Library/VirtualFolders')
    return value if status == 'ok' and isinstance(value, list) else None


def others(folders):
    """Every library except ChromaTube, without the values that change by themselves."""
    return sorted(ja.canonical({k: v for k, v in f.items() if k not in ('RefreshStatus', 'RefreshProgress')}).decode()
                  for f in folders if f.get('Name') != NAME)


def fingerprint_without_libraries(client):
    value, _ = ja.fingerprint(client)
    value.pop('libraries', None)
    return value


def folder_rules(client, server_path, report):
    """Read-only checks of the folder. True when it is fit for the library."""
    folders = libraries(client)
    if folders is None:
        report('FAIL', 'the library list is not readable (an administrator sign-in is needed: --ask-admin)')
        return False
    ok = True
    if any(f.get('Name') == NAME for f in folders):
        report('FAIL', 'a library named ChromaTube already exists')
        ok = False
    locations = [str(p) for f in folders for p in (f.get('Locations') or [])]
    if any(ja.path_within(server_path, loc) or ja.path_within(loc, server_path) for loc in locations):
        report('FAIL', 'the folder is inside (or contains) an existing library folder; use a folder of its own')
        ok = False
    else:
        report('PASS', f'the folder is outside all {len(locations)} existing library folders')
    entries = ja.server_folder_entries(client, server_path)
    if entries is None:
        report('FAIL', 'the server cannot see the folder (wrong path, or not mounted into the Jellyfin container)')
        ok = False
    else:
        report('PASS' if entries else 'INFO', f'the server sees the folder: {len(entries)} entr{"y" if len(entries) == 1 else "ies"}'
               + ('' if entries else ' (empty: start the server tool first, it writes one folder per channel)'))
    return ok


def check(client, report, server_path=None):
    version = ja.server_version(client)
    report('PASS' if version and version >= (10, 9) else 'FAIL', 'server version is 10.9 or newer')
    report('INFO', 'this sign-in is an administrator: ' + ('yes' if client.is_admin else 'no'))
    report('PASS' if client.policy.get('EnableVideoPlaybackTranscoding') else 'FAIL', 'this user may have video converted')
    if server_path:
        folder_rules(client, server_path, report)
    _, shown = ja.fingerprint(client)
    report('INFO', 'server set-up: ' + ', '.join(shown))
    report('INFO', 'nothing on the server was changed by this check')
    return not report.failed


def add(client, report, server_path, apply=False, folder=None):
    if record_file(folder).exists():
        report('FAIL', 'a ChromaTube library is already recorded on this PC; nothing was changed')
        return False
    folder = folder or state_dir()
    record = folder / 'state.json'
    if record.exists():
        report('FAIL', 'a ChromaTube library is already recorded on this PC; nothing was changed')
        return False
    if not folder_rules(client, server_path, report):
        report('INFO', 'nothing was changed')
        return False
    report('INFO', 'would add ONE library: name ChromaTube, type shows, on that one folder; real-time monitoring, '
                   'internet metadata, chapter and trickplay pictures off; no server-wide scan; nothing else')
    if not apply:
        report('INFO', 'dry run: nothing was sent. Run again with --yes to add it')
        return True
    before = libraries(client)
    print_before = fingerprint_without_libraries(client)
    stamp = ja.utc_stamp()
    backup = folder / f'before-add-{stamp}.json'
    ja.save_private(backup, {'taken_utc': stamp, 'libraries': before, 'fingerprint': print_before})
    report('PASS', f'backup saved in your private folder; libraries before: {len(before)}')
    try:
        client.send('POST', '/Library/VirtualFolders', {'name': NAME, 'collectionType': 'tvshows', 'refreshLibrary': 'false'},
                    {'LibraryOptions': dict(OPTIONS, PathInfos=[{'Path': server_path}])})
    except ja.ClientError:
        pass  # judged by what the server now holds
    after = libraries(client) or []
    mine = [f for f in after if f.get('Name') == NAME]
    if len(mine) != 1:
        report('FAIL', 'the library was not added')
        return False
    locations = [str(p) for p in mine[0].get('Locations') or []]
    ja.save_private(record, {'name': NAME, 'item_id': str(mine[0].get('ItemId')), 'path': server_path,
                             'backup': backup.name, 'added_utc': stamp})
    same = others(after) == others(before) and len(after) == len(before) + 1
    right_folder = len(locations) == 1 and ja.same_path(locations[0], server_path)
    report('PASS' if same and right_folder else 'FAIL', 'library ChromaTube added on its folder; every other library is unchanged'
           if same and right_folder else 'library added, but another library changed or the folder is not the one asked')
    unchanged = fingerprint_without_libraries(client) == print_before
    report('PASS' if unchanged else 'FAIL', 'users, devices, plugins, tasks and conversion settings unchanged' if unchanged
           else 'the server fingerprint differs from before')
    report('INFO', 'next: refresh --yes (scans only this library), then test')
    return same and right_folder and unchanged


def manager_record():
    """Chromatic Manager (start-up menu 1.6.5 or newer) records the same library with the same keys here."""
    return ja.private_home('Jellymatic') / 'livetv-backups' / 'chromatube-library.json'


def record_file(folder=None):
    """This tool's record, else Chromatic Manager's, else where this tool would write one."""
    if folder is not None:
        return folder / 'state.json'
    own = state_dir() / 'state.json'
    return own if own.exists() or not manager_record().exists() else manager_record()


def recorded(folder=None):
    record = record_file(folder)
    return json.loads(record.read_text(encoding='utf-8')) if record.exists() else None


def matching_library(client, state):
    folders = libraries(client) or []
    mine = [f for f in folders if f.get('Name') == NAME]
    if len(mine) != 1 or not state:
        return None
    locations = [str(p) for p in mine[0].get('Locations') or []]
    if str(mine[0].get('ItemId')) != state['item_id'] or len(locations) != 1 or not ja.same_path(locations[0], state['path']):
        return None
    return mine[0]


def remove(client, report, apply=False, folder=None):
    record = record_file(folder)
    folder = record.parent
    state = json.loads(record.read_text(encoding='utf-8')) if record.exists() else None
    if not state:
        report('FAIL', 'no ChromaTube library is recorded on this PC; nothing was changed '
                       '(by hand: Dashboard > Libraries > ChromaTube > Remove)')
        return False
    before = libraries(client) or []
    mine = matching_library(client, state)
    if mine is None:
        present = any(f.get('Name') == NAME for f in before)
        report('FAIL' if present else 'INFO', 'the ChromaTube library on the server is not the one recorded (name, id or '
               'folder differ); nothing was changed' if present else 'the ChromaTube library is no longer on the server')
        if not present and apply:
            record.unlink()
        return not present
    report('INFO', 'would remove ONE library: the recorded ChromaTube library (its files are not touched)')
    if not apply:
        report('INFO', 'dry run: nothing was sent. Run again with --yes to remove it')
        return True
    try:
        client.send('DELETE', '/Library/VirtualFolders', {'name': NAME, 'refreshLibrary': 'false'})
    except ja.ClientError:
        pass
    after = libraries(client) or []
    gone = not any(f.get('Name') == NAME for f in after) and others(after) == others(before)
    report('PASS' if gone else 'FAIL', 'library ChromaTube removed; every other library is unchanged (its files were not touched)'
           if gone else 'the library is still there, or another library changed')
    if gone:
        saved = json.loads((folder / state['backup']).read_text(encoding='utf-8')) if (folder / state.get('backup', '')).is_file() \
            else {'libraries': before}
        same_list = others(after) == others(saved['libraries']) and len(after) == len(saved['libraries'])
        report('PASS' if same_list else 'INFO', 'the library list equals the backup from before the add' if same_list
               else 'the library list differs from the day ChromaTube was added (other changes made since)')
        record.unlink()
    return gone


def refresh(client, report, sleep=time.sleep, polls=24, folder=None):
    state = recorded(folder)
    mine = matching_library(client, state)
    if mine is None:
        report('FAIL', 'no recorded ChromaTube library on the server (add it first)')
        return False
    ident = ja.item_id(mine.get('ItemId'))
    client.allowed.append(('POST', re.escape(f'/Items/{ident}/Refresh'), None))
    before, _ = ja.read(client, '/Items', {'userId': client.user_id, 'parentId': ident, 'limit': 200})
    try:
        client.send('POST', f'/Items/{ident}/Refresh', {'Recursive': 'true', 'MetadataRefreshMode': 'Default',
                                                         'ImageRefreshMode': 'Default'})
    except ja.ClientError:
        report('FAIL', 'the server refused the library refresh')
        return False
    count = len((before or {}).get('Items') or [])
    for _ in range(polls):
        sleep(5)
        after, _ = ja.read(client, '/Items', {'userId': client.user_id, 'parentId': ident, 'limit': 200})
        new = len((after or {}).get('Items') or [])
        if new and new >= count:
            count = new
            break
    report('PASS' if count else 'INFO', f'channels in the library: {count}' if count
           else 'no channels yet: is the server tool running and has it written its first list?')
    return True


def test(client, report, seconds=12.0, folder=None):
    state = recorded(folder)
    mine = matching_library(client, state) or next((f for f in libraries(client) or [] if f.get('Name') == NAME), None)
    if mine is None:
        report('FAIL', 'no ChromaTube library')
        return False
    items, _ = ja.read(client, '/Items', {'userId': client.user_id, 'parentId': ja.item_id(mine.get('ItemId')),
                                          'recursive': 'true', 'includeItemTypes': 'Episode,Video,Movie', 'limit': 50,
                                          'sortBy': 'DateCreated', 'sortOrder': 'Descending'})
    found = (items or {}).get('Items') or []
    report('INFO', f'videos in the library: {(items or {}).get("TotalRecordCount", len(found))}')
    if not found:
        report('FAIL', 'no videos in the library yet (refresh --yes after the server tool has listed its channels)')
        return False
    for attempt, item in enumerate(found[:2], 1):
        ident = ja.item_id(item.get('Id'))
        client.allowed.append(('POST', re.escape(f'/Items/{ident}/PlaybackInfo'), None))
        report('INFO', f'trying video {attempt}')
        if ja.play_like_the_console(client, ident, report, seconds=seconds, bitrate=500000, first_limit=20.0):
            report('PASS', 'a ChromaTube video plays through Jellyfin in the Chromatic format')
            return True
    report('FAIL', 'no tried video played in the Chromatic format (see docs/Troubleshooting.md)')
    return False


def status(client, report, folder=None):
    state = recorded(folder)
    folders = libraries(client)
    present = any(f.get('Name') == NAME for f in folders or [])
    report('INFO', f'libraries: {len(folders) if folders is not None else "not readable"}; ChromaTube library present: '
                   f'{"yes" if present else "no"}; recorded on this PC: {"yes" if state else "no"}; '
                   f'matches the record: {"yes" if matching_library(client, state) else "no"}')
    return True


def rules(command):
    if command == 'add':
        return [('POST', r'/Library/VirtualFolders', lambda q, p: q.get('name') == NAME and q.get('refreshLibrary') == 'false')]
    if command == 'remove':
        return [('DELETE', r'/Library/VirtualFolders', lambda q, p: q.get('name') == NAME and q.get('refreshLibrary') == 'false')]
    if command == 'test':
        return [('POST', r'/LiveStreams/Close', None), ('DELETE', r'/Videos/ActiveEncodings', None)]
    return []   # check, status: read-only; refresh adds its one library id after reading it


def main(argv=None):
    parser = argparse.ArgumentParser(description='The one ChromaTube library on your Jellyfin server.')
    parser.add_argument('command', choices=['check', 'add', 'refresh', 'test', 'status', 'remove'])
    parser.add_argument('--server-path', help='the .strm folder as the Jellyfin server sees it')
    parser.add_argument('--yes', action='store_true', help='really change the server (otherwise: a dry run)')
    parser.add_argument('--ask-admin', action='store_true', help='type an administrator sign-in for this run only')
    parser.add_argument('--connection', help='a saved connection file other than the default ones')
    args = parser.parse_args(argv)
    if args.command == 'add' and not args.server_path:
        print('add needs --server-path (the folder as the Jellyfin server sees it).')
        return 2
    if args.command == 'refresh' and not args.yes:
        print('refresh starts a scan of the ChromaTube library. It runs only with --yes.')
        return 2
    report = ja.Report()
    client = ja.open_client(APP, args, rules(args.command), report)
    if client is None:
        return 1
    try:
        if args.command == 'check':
            ok = check(client, report, args.server_path)
        elif args.command == 'add':
            ok = add(client, report, args.server_path, apply=args.yes)
        elif args.command == 'refresh':
            ok = refresh(client, report)
        elif args.command == 'test':
            ok = test(client, report)
        elif args.command == 'status':
            ok = status(client, report)
        else:
            ok = remove(client, report, apply=args.yes)
    finally:
        if client.sign_out_own_session():
            report('INFO', "this run's own sign-in was signed out (no other device or session was touched)")
    return 0 if ok and not report.failed else 1


if __name__ == '__main__':
    raise SystemExit(main())
