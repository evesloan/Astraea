"""Exact, new-only Court A source retention. No engine, Git or publisher calls.

Default operation validates only. --copy must be supplied deliberately by the
authorized parent. Existing or partially created destinations are never reused.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat

TARGET = Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section/source/court_A_completion004')
MANIFEST_NAME = 'RETENTION_MANIFEST.json'
RECEIPT_NAME = 'RETENTION_RECEIPT.json'


def fail(message):
    raise RuntimeError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def check_file(row):
    p = Path(row['source'])
    if not p.is_absolute() or p.is_symlink() or not p.is_file():
        fail('Source must be an existing regular, non-symlink file: ' + str(p))
    if p.stat().st_size != row['bytes'] or sha(p) != row['sha256']:
        fail('Source size/hash mismatch: ' + str(p))


def relative_path(value):
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or any(x in {'', '.', '..'} for x in p.parts) or str(p) != value:
        fail('Unsafe/non-canonical destination: ' + repr(value))
    return p


def validate_context_successor(data):
    """Only the exact old lighting-context guard may move to archived bytes."""
    game = '/workspace/shared/astraea-godot-production-20261003/'
    old_context = {
        game + 'data/architecture/THEATER_RUNTIME_STAGE001.json': 'a056941635b65c03fbcbb2f5075936eae0082fa8bfb0256a2914414d58fa7994',
        game + 'tests/fixtures/THEATER_TEST_FIXTURES.json': 'cad1feb227176f4e24febace8aeb2ff5473f950a95bfe882eebe01a0fd5de0ce',
    }
    historical = data.get('historical_context', [])
    if len(historical) != 2 or {r['original_source']: r['sha256'] for r in historical} != old_context:
        fail('Only the two exact reviewed historical lighting JSONs may be classified')
    old_manifest_rows = [r for r in data['files'] if r['destination_relative'] == 'history/packaging001/RETENTION_MANIFEST.json']
    if len(old_manifest_rows) != 1 or old_manifest_rows[0]['sha256'] != 'ed65e5d9491332dbcdc58896287b2822dd3129ac36976afad0f2426073dca3ad':
        fail('Original exact manifest must be preserved')
    check_file(old_manifest_rows[0])
    old = json.loads(Path(old_manifest_rows[0]['source']).read_text())
    old_pins = {r['source']: (r['bytes'], r['sha256']) for r in old['protected_inputs']}
    new_pins = {r['source']: (r['bytes'], r['sha256']) for r in data['protected_inputs']}
    removed = set(old_pins) - set(new_pins)
    allowed_removed = {game + 'data/architecture/THEATER_RUNTIME_STAGE001.json'}
    if removed != allowed_removed:
        fail('Historical guard transition must remove exactly the original runtime context guard')
    if any(new_pins.get(p) != value for p, value in old_pins.items() if p not in allowed_removed):
        fail('An immutable/original input guard was changed')
    for row in historical:
        matches = [r for r in data['files'] if r['source'] == row['archived_source']]
        if len(matches) != 1 or matches[0]['sha256'] != row['sha256'] or matches[0]['bytes'] != row['bytes']:
            fail('Historical context must be retained as exact payload')
        if not matches[0]['destination_relative'].startswith('historical_game_context002/'):
            fail('Historical context destination must be explicitly classified')
        if new_pins.get(row['archived_source']) != (row['bytes'], row['sha256']):
            fail('Archived historical bytes must remain guarded')
    if game + 'tests/fixtures/THEATER_TEST_FIXTURES.json' in new_pins:
        fail('Historical fixture context must not acquire an unrelated live guard')


def validate(manifest_path, expected):
    manifest_path = Path(manifest_path)
    if len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
        fail('An exact lowercase SHA-256 is required')
    if manifest_path.is_symlink() or sha(manifest_path) != expected:
        fail('Manifest hash mismatch or symlink')
    data = json.loads(manifest_path.read_text())
    if data.get('schema') != 'astraea.court_a.source_retention.v2' or data.get('target') != str(TARGET):
        fail('Unexpected schema or target')
    validate_context_successor(data)
    if not TARGET.parent.is_dir() or TARGET.parent.resolve() != TARGET.parent:
        fail('Target parent missing or symlinked; no parent creation is allowed')
    if os.path.lexists(TARGET):
        fail('REFUSED: destination already exists, including incomplete prior runs: ' + str(TARGET))
    names = {MANIFEST_NAME, RECEIPT_NAME}
    for row in data['files']:
        rel = relative_path(row['destination_relative'])
        if str(rel) in names:
            fail('Duplicate/reserved destination: ' + str(rel))
        names.add(str(rel))
        if row.get('destination') != str(TARGET / rel):
            fail('Destination differs from fixed target plus relative path')
        if os.path.lexists(TARGET / rel):
            fail('REFUSED existing output: ' + str(TARGET / rel))
        check_file(row)
    for name in names:
        if any(str(p) in names for p in PurePosixPath(name).parents if str(p) != '.'):
            fail('File/directory prefix collision: ' + name)
    for row in data['protected_inputs']:
        check_file(row)
    if len(data['files']) != data['payload_file_count'] or sum(r['bytes'] for r in data['files']) != data['payload_bytes']:
        fail('Manifest count/byte summary mismatch')
    return data


def write_new(root_fd, rel, blocks, made):
    """Create with O_EXCL through non-symlink directory descriptors."""
    parts = relative_path(str(rel)).parts
    fd = os.dup(root_fd)
    try:
        current = []
        for part in parts[:-1]:
            current.append(part)
            key = '/'.join(current)
            if key not in made:
                os.mkdir(part, mode=0o755, dir_fd=fd)  # Any existing dir is a refusal.
                made.add(key)
            new_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = new_fd
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        out_fd = os.open(parts[-1], flags, 0o644, dir_fd=fd)
        with os.fdopen(out_fd, 'wb') as out:
            for block in blocks:
                out.write(block)
            out.flush()
            os.fsync(out.fileno())
    finally:
        os.close(fd)


def file_blocks(path):
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            yield block


def retain(manifest_path, expected, do_copy=False):
    manifest_path = Path(manifest_path)
    data = validate(manifest_path, expected)
    summary = {'status': 'PASS_READ_ONLY_PREFLIGHT', 'target': str(TARGET),
               'manifest_sha256': expected, 'payload_files': len(data['files']),
               'payload_bytes': data['payload_bytes'], 'protected_input_count': len(data['protected_inputs']),
               'copied': False}
    if not do_copy:
        return summary
    # No overwrite, rename, cleanup, merge, or fallback target is implemented.
    # A failure intentionally leaves its new partial folder for investigation.
    TARGET.mkdir(mode=0o755, exist_ok=False)
    root_fd = os.open(TARGET, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    made = set()
    try:
        output = []
        for row in data['files']:
            check_file(row)
            rel = row['destination_relative']
            write_new(root_fd, rel, file_blocks(row['source']), made)
            actual = sha(TARGET / rel)
            if actual != row['sha256'] or (TARGET / rel).stat().st_size != row['bytes']:
                fail('Output hash/size mismatch: ' + rel)
            output.append({'path': rel, 'sha256': actual, 'bytes': row['bytes']})
        if sha(manifest_path) != expected:
            fail('Manifest changed during retention')
        write_new(root_fd, MANIFEST_NAME, file_blocks(manifest_path), made)
        if sha(TARGET / MANIFEST_NAME) != expected:
            fail('Copied manifest hash mismatch')
        output.append({'path': MANIFEST_NAME, 'sha256': expected, 'bytes': manifest_path.stat().st_size})
        for row in data['files'] + data['protected_inputs']:
            check_file(row)
        for row in output:
            p = TARGET / row['path']
            if p.is_symlink() or sha(p) != row['sha256'] or p.stat().st_size != row['bytes']:
                fail('Final output verification failed: ' + str(p))
        actual_files = {str(p.relative_to(TARGET)) for p in TARGET.rglob('*') if p.is_file()}
        if actual_files != {r['path'] for r in output}:
            fail('Unexpected file appeared in the new target')
        receipt = {**summary, 'status': 'PASS_NEW_ONLY_SOURCE_RETENTION', 'copied': True,
                   'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'all_original_inputs_unchanged': True, 'output_files_before_receipt': output,
                   'payload_plus_manifest_file_count': len(output),
                   'payload_plus_manifest_bytes': sum(r['bytes'] for r in output),
                   'final_file_count_including_receipt': len(output) + 1,
                   'limits': data['acceptance_limits']}
        encoded = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
        write_new(root_fd, RECEIPT_NAME, [encoded], made)
        receipt_hash = hashlib.sha256(encoded).hexdigest()
        if sha(TARGET / RECEIPT_NAME) != receipt_hash:
            fail('Receipt verification failed')
        return {**summary, 'status': receipt['status'], 'copied': True,
                'final_file_count': len(output) + 1,
                'final_bytes': sum(r['bytes'] for r in output) + len(encoded),
                'receipt_sha256': receipt_hash}
    finally:
        os.close(root_fd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path(__file__).with_name('RETENTION_MANIFEST002.json'))
    parser.add_argument('--expected-manifest-sha256', required=True)
    parser.add_argument('--copy', action='store_true', help='Perform the exact authorized new-only copy; default is read-only validation')
    args = parser.parse_args()
    print(json.dumps(retain(args.manifest, args.expected_manifest_sha256, args.copy), indent=2))
