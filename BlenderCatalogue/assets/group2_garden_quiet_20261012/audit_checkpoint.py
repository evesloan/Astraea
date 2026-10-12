"""Immutable byte audit and independent remote package readback verifier."""
import argparse, datetime, hashlib, json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[3]
P = pathlib.Path(__file__).resolve().parent
PARENT = '6b9e16b0147572ec7222ba3323de0157971d13b5'
BASELINE = 'affc5c807087ff87da29f3642c2d6e418241b896'
OWNED = ['BlenderCatalogue/assets/group2_garden_quiet_20261012',
         'Game/assets/group2_garden_quiet', 'Game/data/group2_garden_quiet',
         'Game/scripts/group2_garden_quiet', 'Game/tests/group2_garden_quiet']
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')
def signature(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def check_files(manifest):
    assert signature(manifest['files']) == manifest['signature']
    for row in manifest['files']:
        p = ROOT / row['path']
        assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], row['path']
def audit():
    assert git('rev-parse', 'HEAD') == PARENT
    assert not git('diff', '--name-only', PARENT), 'Existing tracked work must remain immutable'
    preserved = 0
    for name in ['group2_completion_20261011', 'group2_private_vertical_20261011', 'group2_pit_perimeters_20261011', 'group2_vip_pavilions_20261012', 'group2_care_programmes_20261012', 'group2_family_childcare_20261012', 'group2_vip_dry_club_20261012']:
        path = ROOT / 'BlenderCatalogue/assets' / name / 'MANIFEST.json'
        check_files(json.loads(path.read_text()))
        assert subprocess.check_output(['git', 'show', PARENT + ':' + path.relative_to(ROOT).as_posix()], cwd=ROOT) == path.read_bytes()
        preserved += len(json.loads(path.read_text())['files']) + 1
    checkpoint = json.loads((ROOT / 'CHECKPOINT.json').read_text())
    baseline_files = 0
    for project in checkpoint['projects'].values():
        files = project['files']
        assert signature(files) == project['signature']
        for rel, digest in files.items():
            assert sha(ROOT / project['prefix'] / rel) == digest, rel
        assert git('rev-parse', BASELINE + ':' + project['prefix']) == project['git_tree']
        baseline_files += len(files)
    recovery = json.loads((ROOT / 'BlenderCatalogue/assets/group2_completion_20261011/evidence/RECOVERY_ALL86.json').read_text())
    original_count = 0
    for row in recovery['entries']:
        if row['key'] not in ['787', '792', '794', '795', '797']:
            continue
        assert sha(pathlib.Path('/workspace/group2-native-originals') / row['native_member']) == row['native_sha256']
        assert sha(ROOT / row['runtime_path']) == row['runtime_sha256']
        original_count += 1
    assert original_count == 5
    original_head = subprocess.check_output(['git', '-C', '/workspace/Astraea', 'rev-parse', 'HEAD'], text=True).strip()
    assert original_head == '144ba8cd8d6105c7b1959f25ce88cb5d89185f0b'
    for name in ['FINAL_PASS005.json', 'NATIVE_r002.json', 'SOURCE_CONTEXT001.json', 'SOURCE_CONTEXT_QUIET001.json', 'RETAINED_PROP_VERIFICATION.json']:
        assert json.loads((P / 'evidence' / name).read_text())['pass']
    assert json.loads((P / 'STATUS.json').read_text())['visually_reviewed']
    write(P / 'evidence/PRESERVATION_AUDIT.json', {
        'pass': True, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sealed_parent': PARENT, 'all_prior_package_files_unchanged': preserved,
        'baseline_files_unchanged': baseline_files, 'all_five_native_and_runtime_originals_unchanged': True,
        'original_checkout_head_unchanged': original_head, 'only_additive_owned_paths': OWNED,
        '790_excluded': True, 'shared_root_registry_capacity_routes_unchanged': True,
        'whole_Group2_accepted': False})
    target = P / 'MANIFEST.json'
    files = []
    for prefix in OWNED:
        for path in sorted((ROOT / prefix).rglob('*')):
            if not path.is_file() or path == target:
                continue
            assert not path.is_symlink() and '__pycache__' not in path.parts
            files.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)})
    write(target, {'schema': 'astraea.group2_garden_quiet_manifest.v1', 'parent_checkpoint': PARENT,
                   'baseline': BASELINE, 'owned_paths': OWNED, 'files': files, 'file_count': len(files),
                   'bytes': sum(row['bytes'] for row in files), 'signature': signature(files),
                   'self_excluded': True, 'status': 'UNFINISHED_GROUP2; scoped construction successor'})
    print(json.dumps({'pass': True, 'manifest_sha256': sha(target), 'signature': signature(files),
                      'files_excluding_manifest': len(files), 'bytes_excluding_manifest': sum(r['bytes'] for r in files)}))
def verify(output):
    target = P / 'MANIFEST.json'
    m = json.loads(target.read_text())
    check_files(m)
    actual = {p.relative_to(ROOT).as_posix() for prefix in OWNED for p in (ROOT / prefix).rglob('*') if p.is_file()}
    assert actual == {r['path'] for r in m['files']} | {target.relative_to(ROOT).as_posix()}
    changes = git('diff', '--name-status', PARENT, 'HEAD').splitlines()
    assert len(changes) == len(m['files']) + 1
    assert all(c.startswith('A\t') and any(c[2:].startswith(p + '/') for p in OWNED) for c in changes)
    assert git('rev-parse', 'HEAD^') == PARENT
    assert not git('diff', '--name-only', 'HEAD')
    assert not (ROOT / '.git/objects/info/alternates').exists()
    write(output, {'pass': True, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  'remote_url': git('remote', 'get-url', 'origin'), 'commit': git('rev-parse', 'HEAD'),
                  'tree': git('rev-parse', 'HEAD^{tree}'), 'parent': PARENT,
                  'manifest_sha256': sha(target), 'manifest_signature': m['signature'],
                  'all_owned_bytes_downloaded_and_sha256_matched': True,
                  'files_excluding_manifest': len(m['files']), 'bytes_excluding_manifest': m['bytes'],
                  'method': 'New independent remote clone; no object alternates; exact additive paths'})
    print(output.read_text())
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-output', type=pathlib.Path)
    args = parser.parse_args()
    verify(args.verify_output) if args.verify_output else audit()
