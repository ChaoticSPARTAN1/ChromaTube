# SPDX-License-Identifier: GPL-3.0-or-later
# Additional terms: ADDITIONAL-TERMS.md
"""chromatube_library.py against the fake Jellyfin (which holds other libraries, users and sessions).

Proves: a dry run sends no change; add makes exactly one library with the quiet options and no
server-wide scan, on a folder outside every other library; every other library stays byte-for-byte the
same; refresh scans only that library; test opens a video with PlaybackInfo first and leaves nothing
running; remove refuses when the library is not the recorded one and otherwise deletes only it; only
allow-listed requests are sent; nothing private is printed; a typed-in sign-in signs out only itself.

    py -3 tools/tests/test_chromatube_library.py
"""
import io
import os
import re
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import chromatube_library as tool  # noqa: E402
import fake_jellyfin as fake  # noqa: E402
import jellyfin_admin as ja  # noqa: E402

failures = []
FOLDER = '/config/ChromaTube'


def check(ok, what):
    print(('ok   ' if ok else 'FAIL ') + what)
    if not ok:
        failures.append(what)


def client_for(server, command, typed=False):
    url = f'http://127.0.0.1:{server.server_port}'
    connection = ja.Connection(url, 'owner-name', 'pw-secret-9', '') if typed else ja.Connection(url, '', '', fake.SAVED_TOKEN)
    client = ja.Client(connection, tool.APP, tool.rules(command))
    client.connect()
    return client, url


def private_ok(lines, url):
    text = '\n'.join(f'{k} {t}' for k, t in lines)
    return not [s for s in fake.SECRETS + [url, 'pw-secret-9', FOLDER, 'lib-new', 'vid0'] if s in text]


def others_untouched(state):
    names = [f['Name'] for f in state['libraries']]
    return names[:2] == ['family-movies', 'Shows'] and state['libraries'][0]['LibraryOptions'] == {'EnableRealtimeMonitor': True}


def test_full_cycle(modes, label):
    server, state = fake.start(modes)
    try:
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            report = ja.Report(out=lambda s: None)
            client, url = client_for(server, 'add')
            check(tool.add(client, report, FOLDER, apply=False, folder=folder) and not fake.changing(state),
                  f'{label}: dry run sends no change')
            added = tool.add(client, report, FOLDER, apply=True, folder=folder)
            if 'library-add-refused' in modes:
                check(not added and not (folder / 'state.json').exists() and len(state['libraries']) == 2,
                      f'{label}: a refused add records nothing')
            else:
                mine = state['libraries'][-1]
                options = mine['LibraryOptions']
                check(added and mine['Name'] == 'ChromaTube' and mine['Locations'] == [FOLDER] and mine['CollectionType'] == 'tvshows',
                      f'{label}: one library ChromaTube on the folder asked')
                check(options['EnableRealtimeMonitor'] is False and options['EnableInternetProviders'] is False
                      and options['EnableTrickplayImageExtraction'] is False and state['library_scans'] == 0,
                      f'{label}: quiet options and no server-wide scan')
                check(not tool.add(client, report, FOLDER, apply=True, folder=folder), f'{label}: a second add is refused')
                client_r, _ = client_for(server, 'refresh')
                tool.refresh(client_r, report, sleep=lambda s: None, polls=2, folder=folder)
                check(state['refreshed'] == ['lib-new'], f'{label}: refresh scans only the ChromaTube library')
                client_t, _ = client_for(server, 'test')
                played = tool.test(client_t, report, seconds=0.2, folder=folder)
                check(played == ('no-videos' not in modes), f'{label}: test plays a video in the Chromatic format' if 'no-videos' not in modes
                      else f'{label}: test says there are no videos yet')
                check(not state['open'], f'{label}: nothing left open')
                client_d, _ = client_for(server, 'remove')
                check(tool.remove(client_d, report, apply=False, folder=folder) and len(state['libraries']) == 3,
                      f'{label}: remove dry run deletes nothing')
                removed = tool.remove(client_d, report, apply=True, folder=folder)
                if 'library-delete-fails' in modes:
                    check(not removed and (folder / 'state.json').exists(), f'{label}: a failed remove keeps its record')
                else:
                    check(removed and len(state['libraries']) == 2 and not (folder / 'state.json').exists(),
                          f'{label}: remove deletes exactly the recorded library')
            allowed = [('POST', r'/Library/VirtualFolders'), ('DELETE', r'/Library/VirtualFolders'), ('POST', r'/Items/lib-new/Refresh'),
                       ('POST', r'/Items/vid\d/PlaybackInfo'), ('POST', r'/LiveStreams/Close'), ('DELETE', r'/Videos/ActiveEncodings')]
            check(all(any(m == a and re.fullmatch(p, path) for a, p in allowed) for m, path in fake.changing(state))
                  and not state['unexpected'], f'{label}: only allow-listed requests were sent')
            check(others_untouched(state), f'{label}: the other libraries were never touched')
            check(private_ok(report.lines, url), f'{label}: nothing private printed')
            check(not state['logouts'], f'{label}: a saved token is never signed out')
    finally:
        server.shutdown()
        server.server_close()


def test_folder_rules():
    server, state = fake.start()
    try:
        with tempfile.TemporaryDirectory() as folder:
            client, _ = client_for(server, 'add')
            report = ja.Report(out=lambda s: None)
            inside_library = tool.add(client, report, '/srv/private/media/tv/ChromaTube', apply=True, folder=Path(folder))
            check(not inside_library and len(state['libraries']) == 2, 'a folder inside an existing library is refused')
            hidden = tool.add(client, report, '/nowhere/ChromaTube', apply=True, folder=Path(folder))
            check(not hidden and not fake.changing(state), 'a folder the server cannot see is refused, nothing sent')
    finally:
        server.shutdown()
        server.server_close()


def test_record_mismatch():
    server, state = fake.start()
    try:
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            client, _ = client_for(server, 'add')
            report = ja.Report(out=lambda s: None)
            tool.add(client, report, FOLDER, apply=True, folder=folder)
            state['libraries'][-1]['ItemId'] = 'someone-elses'       # the library was replaced by hand since
            client_d, _ = client_for(server, 'remove')
            check(not tool.remove(client_d, report, apply=True, folder=folder) and len(state['libraries']) == 3
                  and ('DELETE', '/Library/VirtualFolders') not in fake.changing(state),
                  'remove refuses when the library is not the recorded one')
            try:
                client_d.send('DELETE', '/Library/VirtualFolders', {'name': 'family-movies', 'refreshLibrary': 'false'})
                refused = False
            except ja.ClientError:
                refused = True
            check(refused and state['libraries'][0]['Name'] == 'family-movies', 'deleting any other library is refused unsent')
    finally:
        server.shutdown()
        server.server_close()


def test_typed_sign_in():
    server, state = fake.start()
    try:
        client, url = client_for(server, 'check', typed=True)
        report = ja.Report(out=lambda s: None)
        tool.check(client, report, FOLDER)
        check(fake.changing(state) == [('POST', '/Users/AuthenticateByName')], 'check: reads only (after the sign-in)')
        check(client.sign_out_own_session() and state['logouts'] == [fake.OWN_TOKEN], 'a typed-in sign-in signs out only itself')
        check(private_ok(report.lines, url), 'check: nothing private printed')
    finally:
        server.shutdown()
        server.server_close()


def test_manager_record():
    """A library recorded by Chromatic Manager (same keys, Jellymatic's folder) is removed by its record."""
    import json
    server, state = fake.start()
    try:
        state['libraries'].append({'Name': 'ChromaTube', 'ItemId': 'lib-mgr', 'CollectionType': 'tvshows',
                                   'Locations': [FOLDER], 'LibraryOptions': {}})
        record = tool.manager_record()
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(json.dumps({'name': 'ChromaTube', 'item_id': 'lib-mgr', 'path': FOLDER, 'backup': 'none.json'}),
                          encoding='utf-8')
        report = ja.Report(out=lambda s: None)
        client, _ = client_for(server, 'add')
        check(not tool.add(client, report, FOLDER, apply=True) and len(state['libraries']) == 3,
              "a library recorded by Chromatic Manager is never added twice")
        client_d, _ = client_for(server, 'remove')
        check(tool.remove(client_d, report, apply=True) and [f['Name'] for f in state['libraries']] == ['family-movies', 'Shows']
              and not record.exists(), "Chromatic Manager's recorded library is removed by its record, nothing else")
    finally:
        server.shutdown()
        server.server_close()


def test_command_line():
    out = io.StringIO()
    with redirect_stdout(out):
        codes = [tool.main(['add']), tool.main(['refresh'])]
    check(codes == [2, 2], 'the command line refuses add without a folder and refresh without --yes')


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='chromatube-test-') as home:
        os.environ['CHROMATUBE_HOME'] = home       # never the real private folders
        os.environ['JELLYMATIC_HOME'] = os.path.join(home, 'jellymatic')
        test_full_cycle(set(), 'add/refresh/test/remove')
        test_full_cycle({'live'}, 'video opened as a live stream')
        test_full_cycle({'no-videos'}, 'no videos yet')
        test_full_cycle({'library-add-refused'}, 'add refused')
        test_full_cycle({'library-delete-fails'}, 'delete fails')
        test_folder_rules()
        test_record_mismatch()
        test_typed_sign_in()
        test_manager_record()
        test_command_line()
    print('PASS' if not failures else f'FAIL: {len(failures)} check(s) failed')
    sys.exit(1 if failures else 0)
