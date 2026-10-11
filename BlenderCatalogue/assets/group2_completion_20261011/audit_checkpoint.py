"""Audit immutable baseline/source bytes, or independently verify this package.

The manifest excludes itself to avoid a circular digest. Its own SHA256 and
the exact commit/tree are recorded by the independent publication verifier.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
PACKAGE = pathlib.Path(__file__).resolve().parent
BASELINE = 'affc5c807087ff87da29f3642c2d6e418241b896'
SOURCE = 'ae925fbb839a48c44f82f999a0687727283d70a4'
OWNED = ['BlenderCatalogue/assets/group2_completion_20261011',
         'Game/assets/group2_completion', 'Game/data/group2_completion',
         'Game/scripts/group2_completion', 'Game/tests/group2_completion']

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            digest.update(chunk)
    return digest.hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def audit(native_root):
    assert git('rev-parse', 'HEAD') == BASELINE, 'Create initial manifest before committing'
    changed = git('diff', '--name-status', BASELINE).splitlines()
    assert all(line.startswith('A\t') and any(line[2:].startswith(p + '/') for p in OWNED)
               for line in changed), 'An existing baseline path changed'
    baseline = json.loads((ROOT / 'CHECKPOINT.json').read_text())
    projects = {}
    for name, project in baseline['projects'].items():
        files = project['files']
        signature = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        assert signature == project['signature']
        for rel, expected in files.items():
            path = ROOT / project['prefix'] / rel
            assert path.is_file() and sha(path) == expected, str(path)
        tree = git('rev-parse', BASELINE + ':' + project['prefix'])
        assert tree == project['git_tree']
        projects[name] = {'files': len(files), 'all_sha256_match': True,
                          'baseline_tree': tree, 'manifest_signature': signature}
    original_head = subprocess.check_output(['git', '-C', '/workspace/Astraea', 'rev-parse', 'HEAD'], text=True).strip()
    assert original_head == '144ba8cd8d6105c7b1959f25ce88cb5d89185f0b'
    recovery = json.loads((PACKAGE / 'evidence/RECOVERY_ALL86.json').read_text())
    assert recovery['source_ref'] == SOURCE and recovery['count'] == 86 and recovery['pass']
    source_totals = {'sections': 0, 'archive_dependency_members_rehashed': 0,
                     'native_bytes': 0, 'runtime_bytes': 0}
    for row in recovery['entries']:
        native = native_root / row['native_member']
        assert sha(native) == row['native_sha256']
        runtime = ROOT / row['runtime_path']
        assert sha(runtime) == row['runtime_sha256']
        assert sha(ROOT / 'Game/data/group2_completion/contracts' / (row['key'] + '.json')) == row['contract_sha256']
        assert row['all_pinned_archive_members_rehashed'] > 0
        for item in row['retained_evidence']:
            path = ROOT / item['path']
            assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
        source_totals['sections'] += 1
        source_totals['archive_dependency_members_rehashed'] += row['all_pinned_archive_members_rehashed']
        source_totals['native_bytes'] += native.stat().st_size
        source_totals['runtime_bytes'] += runtime.stat().st_size
    for name in ['FULL_PACKAGE_PASS.json', 'INTERACTION_FINAL_PASS.json', 'LIGHTING_PASS.json',
                 'FLOOR_INTERFACE_VERIFICATION.json', 'FLOOR_NATIVE_r001.json',
                 'STAR_ATLAS_CURRENT_INTERFACE.json']:
        result = json.loads((PACKAGE / 'evidence' / name).read_text())
        assert result['pass'], name
    floor = json.loads((ROOT / 'Game/data/group2_completion/FLOOR_INTERFACE.json').read_text())
    assert floor['790_excluded'] and not floor['production_adoption']
    assert not floor['new_units'] and not floor['new_decks']
    assert floor['structural_preimage_sha256'] == sha(ROOT / 'Game/data/generated/structural_meshes.json')
    write(PACKAGE / 'evidence/FINAL_PRESERVATION_AUDIT.json', {
        'pass': True, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'baseline_commit': BASELINE, 'baseline_root_tree': git('rev-parse', BASELINE + '^{tree}'),
        'original_checkout_head_unchanged': original_head, 'baseline_projects': projects,
        'retained_source_commit': SOURCE, 'unchanged_sources': source_totals,
        'protected_790_excluded': True, 'only_new_group_paths': OWNED,
        'production_registries_root_capacity_and_protected_geometry_changed': False})
    manifest_path = PACKAGE / 'MANIFEST.json'
    files = []
    for prefix in OWNED:
        for path in sorted((ROOT / prefix).rglob('*')):
            if not path.is_file() or path == manifest_path:
                continue
            assert not path.is_symlink(), 'Package must have ordinary independent bytes'
            files.append({'path': path.relative_to(ROOT).as_posix(),
                          'bytes': path.stat().st_size, 'sha256': sha(path)})
    signature = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    write(manifest_path, {'schema': 'astraea.group2_completion_manifest.v1',
                         'baseline_commit': BASELINE, 'retained_source_commit': SOURCE,
                         'owned_paths': OWNED, 'files': files, 'file_count': len(files),
                         'bytes': sum(row['bytes'] for row in files),
                         'signature_algorithm': "SHA256 of UTF-8 json.dumps(files,sort_keys=True,separators=(',',':'))",
                         'signature': signature, 'self_excluded': True,
                         'status': 'UNFINISHED_GROUP2; scoped opt-in construction handoff'})
    print(json.dumps({'pass': True, 'baseline_files': sum(p['files'] for p in projects.values()),
                      'sources': source_totals, 'package_files': len(files),
                      'manifest_sha256': sha(manifest_path), 'signature': signature}))

def verify(output):
    manifest_path = PACKAGE / 'MANIFEST.json'
    manifest = json.loads(manifest_path.read_text())
    files = manifest['files']
    assert hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == manifest['signature']
    assert len(files) == manifest['file_count']
    actual_paths = {path.relative_to(ROOT).as_posix() for prefix in OWNED
                    for path in (ROOT / prefix).rglob('*') if path.is_file()}
    assert actual_paths == {row['path'] for row in files} | {manifest_path.relative_to(ROOT).as_posix()}
    for row in files:
        path = ROOT / row['path']
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], row['path']
    head = git('rev-parse', 'HEAD')
    changed = git('diff', '--name-status', BASELINE, head).splitlines()
    assert len(changed) == len(files) + 1
    assert all(line.startswith('A\t') and any(line[2:].startswith(p + '/') for p in OWNED) for line in changed)
    assert not git('diff', '--name-only', head)
    write(output, {'pass': True, 'verification_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'remote_url': git('remote', 'get-url', 'origin'), 'commit': head,
                   'root_tree': git('rev-parse', 'HEAD^{tree}'), 'parent': git('rev-parse', 'HEAD^'),
                   'all_owned_file_bytes_downloaded_and_sha256_matched': True,
                   'manifest_sha256': sha(manifest_path), 'manifest_signature': manifest['signature'],
                   'files_excluding_manifest': len(files), 'bytes_excluding_manifest': manifest['bytes'],
                   'all_changed_paths_additive_and_group_owned': True,
                   'method': 'New independent remote clone; no local object alternates; sparse owned paths read back'})
    print(output.read_text())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', type=pathlib.Path)
    parser.add_argument('--verify-output', type=pathlib.Path)
    args = parser.parse_args()
    if args.verify_output:
        verify(args.verify_output)
    else:
        assert args.native_root
        audit(args.native_root)
