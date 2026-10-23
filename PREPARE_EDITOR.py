#!/usr/bin/env python3
"""Prepare only pinned missing Astraea editor inputs. Python 3.9+, no dependencies.
Run from a fresh construction-branch checkout, with Godot closed:
    python PREPARE_EDITOR.py
    python PREPARE_EDITOR.py --check-only
This never applies code patches, overwrites survivors, imports, or launches engines.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

INPUTS_SHA256 = '4bd9e73cb7013da1a07afa903d8759e25eb375ca7ba08e2a9a0ba02b4a7a025a'
CHUNK = 4 * 1024 * 1024


class Refused(ValueError):
    pass


def inside(root, relative):
    """No symlinks, Windows alternate streams, drive paths, or traversal."""
    if not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative:
        raise Refused('Unsafe path: ' + repr(relative))
    parts = relative.split('/')
    if any(p in ('', '.', '..') for p in parts) or PurePosixPath(relative).is_absolute():
        raise Refused('Unsafe path: ' + relative)
    p = root
    for part in parts:
        p = p / part
        if p.is_symlink():
            raise Refused('Symlink refused: ' + relative)
        # Windows directory junctions are reparse points, not always symlinks.
        if os.path.lexists(p) and getattr(p.lstat(), 'st_file_attributes', 0) & 0x400:
            raise Refused('Reparse point refused: ' + relative)
    return p


def hashes(path):
    size = path.stat().st_size
    h = hashlib.sha256()
    g = hashlib.sha1(('blob ' + str(size) + '\0').encode())
    with path.open('rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
            g.update(b)
    return size, h.hexdigest(), g.hexdigest()


def verify_file(root, row):
    path = inside(root, row['path'])
    if not os.path.lexists(path):
        return False
    if not stat.S_ISREG(path.lstat().st_mode):
        raise Refused('Not a regular file: ' + row['path'])
    size, sha, git = hashes(path)
    if size != row['bytes'] or sha != row['sha256'] or (row.get('git_blob_sha1') and git != row['git_blob_sha1']):
        raise Refused('Existing hash/length conflict (preserved): ' + row['path'])
    return True


def read_pinned(root, row):
    if not verify_file(root, row):
        raise Refused('Required pinned file missing: ' + row['path'])
    raw = inside(root, row['path']).read_bytes()
    # Close the read-after-verify race for configuration bytes.
    if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
        raise Refused('Pinned file changed while reading: ' + row['path'])
    return raw


def unique_rows(rows):
    result = {}
    casefold = {}
    for row in rows:
        name = row['path']
        if name.casefold() in casefold and casefold[name.casefold()] != name:
            raise Refused('Case-colliding paths: ' + name)
        casefold[name.casefold()] = name
        if name in result and (row['sha256'], row['bytes']) != (result[name]['sha256'], result[name]['bytes']):
            raise Refused('Conflicting definitions: ' + name)
        result[name] = row
    return result


def load_inputs(repo):
    raw = inside(repo, 'PREPARE_EDITOR_INPUTS.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != INPUTS_SHA256:
        raise Refused('PREPARE_EDITOR_INPUTS.json hash mismatch')
    pins = json.loads(raw)
    read_pinned(repo, pins['project'])
    contracts = json.loads(read_pinned(repo, pins['manifest']))
    if len(contracts) != pins['manifest']['entries']:
        raise Refused('Manifest entry count mismatch')
    canonical = unique_rows(pins['canonical'])
    if len(canonical) != 80:
        raise Refused('Canonical repair count mismatch')
    for row in canonical.values():
        if not verify_file(repo, row):
            raise Refused('Canonical repair missing; this is not a patch installer: ' + row['path'])
    rows = []
    for row in contracts:
        if not row['path'].startswith('res://'):
            raise Refused('Invalid contract path')
        rows.append(dict(row, path='Game/' + row['path'][6:]))
    required = unique_rows(rows)
    if len(required) != len(contracts):
        raise Refused('Duplicate manifest path')
    supplement = json.loads(read_pinned(repo, pins['supplement']))
    if len(supplement['files']) != pins['supplement']['entries']:
        raise Refused('Supplement count mismatch')
    recipes = {}
    base = str(PurePosixPath(pins['supplement']['path']).parent)
    for row in supplement['files']:
        target = 'Game/' + row['path'][6:]
        expected = required.get(target)
        if not row['path'].startswith('res://') or expected is None or (row['sha256'], row['bytes']) != (expected['sha256'], expected['bytes']):
            raise Refused('Supplement/final manifest disagreement: ' + target)
        recipe = dict(row, path=target)
        if 'payload' in row:
            recipe['retained_path'] = base + '/' + row['payload']
        else:
            alternate = pins['png_sources'].get(row['sha256'])
            if alternate:
                recipe['alternate'] = alternate['path']
                recipe['git_blob_sha1'] = alternate['git_blob_sha1']
        if target in recipes:
            raise Refused('Duplicate supplement target: ' + target)
        recipes[target] = recipe
    for row in pins['retained_additions']:
        if row['path'] in recipes:
            raise Refused('Duplicate retained target: ' + row['path'])
        recipes[row['path']] = row
    required = unique_rows(list(required.values()) + pins['retained_additions'] + list(canonical.values()) + [pins['project']])
    for row in required.values():
        inside(repo, row['path'])
    if len(recipes) != 3161:
        raise Refused('Preparation target count mismatch')
    return pins, required, recipes


def inspect_targets(repo, required, recipes):
    missing = []
    unexpected = []
    for row in required.values():
        if not verify_file(repo, row):
            if row['path'] not in recipes:
                unexpected.append(row['path'])
            else:
                missing.append(row['path'])
    if unexpected:
        raise Refused('Missing files outside preparation recipes (' + str(len(unexpected)) + '): ' + '; '.join(unexpected))
    return missing


def copy_stream(reader, writer, count=None):
    remaining = count
    while remaining is None or remaining:
        b = reader.read(CHUNK if remaining is None else min(CHUNK, remaining))
        if not b:
            if remaining:
                raise Refused('Unexpected end of retained source')
            break
        writer.write(b)
        if remaining is not None:
            remaining -= len(b)


def stage_sources(repo, recipes, missing, stage):
    """Resolve and hash every needed byte before any destination is created."""
    cached = {}
    verified_glbs = set()
    result = {}
    for name in missing:
        row = recipes[name]
        key = (row['sha256'], row['bytes'])
        if key in cached:
            result[name] = cached[key]
            continue
        dest = stage / ('content-' + row['sha256'])
        with dest.open('xb') as w:
            alternate = inside(repo, row['alternate']) if row.get('alternate') else None
            retained = row.get('retained_path')
            if alternate is not None and os.path.lexists(alternate):
                # Wrong existing alternates are conflicts, never silently skipped.
                verify_file(repo, dict(row, path=row['alternate']))
                with alternate.open('rb') as f:
                    copy_stream(f, w)
            elif retained:
                source = inside(repo, retained)
                if not verify_file(repo, dict(row, path=retained)):
                    raise Refused('Retained source missing: ' + retained)
                with source.open('rb') as f:
                    copy_stream(f, w)
            elif 'archive' in row:
                archive = inside(repo, row['archive'])
                inside(repo, row['member'])  # Reject unsafe member names; no extractall.
                with zipfile.ZipFile(archive) as z:
                    matches = [i for i in z.infolist() if i.filename == row['member']]
                    if len(matches) != 1 or matches[0].file_size != row['bytes'] or matches[0].is_dir():
                        raise Refused('ZIP member missing/ambiguous/wrong length: ' + row['member'])
                    with z.open(matches[0]) as f:
                        copy_stream(f, w)
            else:
                source = inside(repo, row['source'])
                if row['source'] not in verified_glbs:
                    if hashes(source)[1] != row['source_sha256']:
                        raise Refused('Retained GLB hash conflict: ' + row['source'])
                    verified_glbs.add(row['source'])
                offset, length = row['offset'], row['length']
                if offset < 0 or length != row['bytes'] or offset + length > source.stat().st_size:
                    raise Refused('Invalid embedded image range: ' + name)
                with source.open('rb') as f:
                    f.seek(offset)
                    copy_stream(f, w, length)
            w.flush()
            os.fsync(w.fileno())
        actual = dict(row, path=dest.name)
        verify_file(stage, actual)
        cached[key] = dest
        result[name] = dest
    return result


def create_missing(repo, recipes, staged, stage):
    created = 0
    for index, (name, source) in enumerate(staged.items()):
        row = recipes[name]
        target = inside(repo, name)
        if verify_file(repo, row):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target = inside(repo, name)
        # One separate inode per destination. Atomic no-replace publication via
        # hard link prevents crash-truncated targets and dedup edit coupling.
        candidate = stage / ('publish-' + str(index))
        shutil.copyfile(source, candidate)
        with candidate.open('rb') as f:
            os.fsync(f.fileno())
        verify_file(stage, dict(row, path=candidate.name))
        try:
            os.link(candidate, target)
            created += 1
        except FileExistsError:
            if not verify_file(repo, row):
                raise Refused('Concurrent destination conflict: ' + name)
        except OSError as e:
            raise Refused('Atomic missing-only creation unavailable; preserved targets: ' + name + ': ' + str(e)) from e
        finally:
            candidate.unlink()
        verify_file(repo, row)
    return created


def source_commit(repo):
    try:
        return subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL, text=True, timeout=10).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def run(repo, check_only=False):
    pins, required, recipes = load_inputs(repo)
    lock = inside(repo, '.astraea-prepare-editor.lock')
    if check_only:
        if os.path.lexists(lock):
            raise Refused('Preparation lock exists; check again after the preparer exits')
        missing = inspect_targets(repo, required, recipes)
        # Strictly read-only: source-byte staging occurs only during preparation.
        return receipt(repo, pins, missing, 0, not missing, check_only=True)
    try:
        lock.mkdir()
    except FileExistsError as e:
        raise Refused('Preparation lock exists. Do not run concurrently. After a crash, confirm no preparer is running before removing only this lock directory.') from e
    try:
        missing = inspect_targets(repo, required, recipes)
        with tempfile.TemporaryDirectory(prefix='.astraea-prepare-', dir=repo) as temp:
            stage = Path(temp)
            staged = stage_sources(repo, recipes, missing, stage)
            # Recheck all survivors immediately before the first target write.
            inspect_targets(repo, required, recipes)
            created = create_missing(repo, recipes, staged, stage)
            if inspect_targets(repo, required, recipes):
                raise Refused('Post-write verification still has missing inputs')
        return receipt(repo, pins, missing, created, True)
    finally:
        lock.rmdir()


def receipt(repo, pins, missing, created, complete, check_only=False):
    return {'status': 'SOURCE_PREPARATION_PASS' if complete else 'PREPARATION_REQUIRED',
            'source_commit': source_commit(repo), 'source_branch_expected': pins['source_branch'],
            'manifest_sha256': pins['manifest']['sha256'], 'manifest_entries': pins['manifest']['entries'],
            'canonical_repairs_verified': 80, 'retained_targets': 11,
            'missing_before': len(missing), 'created': created, 'existing_files_overwritten': 0,
            'all_required_source_hashes_match': complete, 'check_only': check_only,
            'engine_started': False, 'playable_build_accepted': False,
            'scope': 'Pinned source preparation only, not full native/runtime closure or startup validation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--check-only', action='store_true', help='Read-only target verification; writes nothing')
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    result = run(repo, args.check_only)
    print(json.dumps(result, indent=2))
    return 0 if result['all_required_source_hashes_match'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as e:
        print('REFUSED: ' + str(e), file=sys.stderr)
        sys.exit(2)
