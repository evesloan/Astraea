"""Seal owned R008 additions while verifying baseline and every immutable prior blob."""
from pathlib import Path
import json, hashlib, subprocess

P = Path(__file__).resolve().parents[1]
C = P.parent
R = C.parents[1]
BASE = 'affc5c807087ff87da29f3642c2d6e418241b896'
PREVIOUS = '2ecabfcaa56375f63eacf7851a0a34b12089e9be'
OLD = C.parent / 'group7_hull_atrium_20261009'
manifest_path = C.relative_to(R).as_posix() + '/RESOURCE_HASHES.json'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=R)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

baseline = json.loads((R / 'CHECKPOINT.json').read_text())
counts = {}
for label, project in baseline['projects'].items():
    for name, want in project['files'].items():
        assert sha(R / project['prefix'] / name) == want, (label, name)
    counts[label] = len(project['files'])
prior = 0
for line in git('ls-tree', '-r', '7f9f4777a4ae93884282155ea9d05b6ff125bd57', '--', OLD.relative_to(R).as_posix()).decode().splitlines():
    meta, name = line.split('\t', 1)
    blob = meta.split()[2]
    content = (R / name).read_bytes()
    assert hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() == blob, name
    prior += 1
previous_raw = git('show', PREVIOUS + ':' + manifest_path)
previous = json.loads(previous_raw)
assert hashlib.sha256(previous_raw).hexdigest() == '679d231e51a1113255508273045efe2bf914e83ddcdfe015ed666e27c72861a2'
allowed = {'Game/data/architecture/GROUP7_COMPLETION.json',
                      C.relative_to(R).as_posix() + '/docs/HANDOFF.md'}
changed = []
for name, row in previous['files'].items():
    if sha(R / name) != row['sha256']:
        assert name in allowed, name
        changed.append(name)
assert all(line.split('\t', 1)[0] == 'A' for line in git('diff', '--name-status', BASE).decode().splitlines())
assert git('rev-parse', 'HEAD').decode().strip() == PREVIOUS
saved = '/workspace/Astraea'
assert subprocess.check_output(['git', 'status', '--porcelain', '-uno'], cwd=saved) == b''
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=saved).decode().strip() == '144ba8cd8d6105c7b1959f25ce88cb5d89185f0b'
proof = {'status': 'PASS', 'baseline_commit': BASE,
         'baseline_tree': git('rev-parse', BASE + '^{tree}').decode().strip(),
         'baseline_sha256_files': counts, 'prior_git_blobs_exact': prior,
         'previous_checkpoint': PREVIOUS, 'previous_manifest_files': len(previous['files']),
         'unchanged_previous_manifest_files': len(previous['files']) - len(changed),
         'declared_owned_runtime_document_successors': changed,
         'source_originals_changed': 0, 'saved_checkout_untouched': True,
         'shared_root_registry_edits': 0, 'capacity_delta': 0, 'new_room_ids': 0}
(P / 'qa/PRESERVATION_CHECK.json').write_text(json.dumps(proof, indent=2) + '\n')
paths = set(previous['files'])
for name in git('ls-files', '--others', '--exclude-standard', '-z').decode().split('\0'):
    if not name:
        continue
    owned = name.startswith(P.relative_to(R).as_posix() + '/') or name.startswith('Game/assets/models/G7_Completion_R008') or any(name == 'Game/tests/' + test + suffix for test in ['group7_theater_weatherline_check', 'group7_actual_width_receivers'] for suffix in ['.gd', '.gd.uid'])
    if owned:
        paths.add(name)
paths.discard(manifest_path)
files = {}
for name in sorted(paths):
    p = R / name
    assert p.is_file()
    size = p.stat().st_size
    assert size < 95 * 1024 * 1024, (name, size)
    files[name] = {'sha256': sha(p), 'bytes': size}
aggregate = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
manifest = {**previous, 'files': files, 'files_aggregate_sha256': aggregate,
            'file_count': len(files), 'total_bytes': sum(x['bytes'] for x in files.values()),
            'selected_revision': 'R008 theater weatherline and canonical owned foot plus retained R007B/R006B/R005B/R004/R003 construction',
            'previous_checkpoint': PREVIOUS}
(C / 'RESOURCE_HASHES.json').write_text(json.dumps(manifest, indent=2) + '\n')
Path('/tmp/astraea_group7_r008_owned_paths.nul').write_bytes('\0'.join(sorted(paths | {manifest_path})).encode() + b'\0')
print(json.dumps({'status': 'PASS', 'baseline_files': sum(counts.values()),
                  'prior_blobs': prior, 'files': len(files), 'bytes': manifest['total_bytes'],
                  'manifest_sha256': sha(C / 'RESOURCE_HASHES.json'), 'aggregate_sha256': aggregate}))
