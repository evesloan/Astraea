#!/usr/bin/env python3
"""Portable exact historical fixture preparation. No engine/import/network calls.
Uses only PORTABLE_INPUTS.json, supplied checkout/PCK, and captured import bytes.
Never edits the checkout or overwrites conflicting prepared files.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import pck_inputs

HERE = Path(__file__).resolve().parent

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(16 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def relative(value):
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('Unsafe manifest-relative path: ' + value)
    return Path(*path.parts)

def verify(data, row):
    if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
        raise ValueError('Exact historical byte mismatch: ' + row['uri'])
    if row.get('git_blob_sha1'):
        git = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if git != row['git_blob_sha1']:
            raise ValueError('Git blob mismatch: ' + row['uri'])

def write_exact(path, data):
    if path.exists():
        if not path.is_file() or path.read_bytes() != data:
            raise ValueError('Refuse overwrite: ' + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True,
                        help='Checkout root containing Game/. Missing/mismatched files use exact retained bytes, never overwrite checkout.')
    parser.add_argument('--base-pack', type=Path, required=True,
                        help='Retained Astraea-e3af0334.pck; complete SHA256 must match.')
    parser.add_argument('--out', type=Path, default=HERE / 'prepared',
                        help='Separate disposable preparation directory (default: ./prepared beside helper).')
    args = parser.parse_args()
    repo, pack, out = args.repo.resolve(), args.base_pack.resolve(), args.out.resolve()
    contract_path = HERE / 'PORTABLE_INPUTS.json'
    contract = json.loads(contract_path.read_text())
    assert contract['schema'] == 1 and contract['input_count'] == 114
    assert contract['source_commit'] == '448eab129169f3c205e7db0662fcf774b869a346'
    if pack.stat().st_size != contract['pack']['bytes'] or sha256_file(pack) != contract['pack']['sha256']:
        raise ValueError('Retained PCK hash/length mismatch; no inputs prepared')
    index = pck_inputs.index(pack)['entries']
    if len(index) != contract['pack']['entry_count']:
        raise ValueError('Retained PCK entry-count mismatch')
    mapping, choices = [], []
    with pack.open('rb') as stream:
        def read_entry(expected):
            actual = index.get(expected['path'])
            if actual is None or any(actual[k] != expected[k] for k in ['path', 'offset', 'bytes', 'md5']):
                raise ValueError('PCK index mismatch: ' + expected['path'])
            stream.seek(actual['offset'])
            data = stream.read(actual['bytes'])
            if hashlib.md5(data).hexdigest() != expected['md5']:
                raise ValueError('PCK entry checksum mismatch: ' + expected['path'])
            if expected.get('sha256') and hashlib.sha256(data).hexdigest() != expected['sha256']:
                raise ValueError('PCK entry SHA256 mismatch: ' + expected['path'])
            return data
        for row in contract['inputs']:
            candidate = repo / relative(row['repository_path'])
            name = relative(row['uri'].removeprefix('res://'))
            # Verify exact retained recovery bytes even when the checkout supplies this input.
            if 'captured_import_policy_utf8' in row:
                fallback = row['captured_import_policy_utf8'].encode('utf-8')
                exported = read_entry(row['retained_export_remap'])
                for key in [b'type', b'uid', b'path']:
                    pattern = rb'^' + key + rb'=([^\n\x00]+)'
                    if re.search(pattern, exported, re.M)[1] != re.search(pattern, fallback, re.M)[1]:
                        raise ValueError('Import remap differs: ' + row['uri'])
                read_entry(row['retained_imported_resource'])
                fallback_kind = 'captured_tested_import_policy'
            else:
                fallback = read_entry(row['verified_pck_entry'])
                fallback_kind = 'verified_retained_pck_entry'
            verify(fallback, row)
            checkout_state = 'missing'
            source = None
            if candidate.is_file():
                data = candidate.read_bytes()
                if len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']:
                    verify(data, row)
                    source, checkout_state = candidate, 'exact_historical_match'
                else:
                    checkout_state = 'different_preserved_unchanged'
            if source is None:
                source = out / 'inputs' / name
                write_exact(source, fallback)
                kind = fallback_kind
            else:
                kind = 'supplied_checkout'
            mapping.append({'path': row['uri'], 'source': str(source), 'sha256': row['sha256'], 'bytes': row['bytes']})
            choices.append({'uri': row['uri'], 'source_kind': kind, 'checkout_state': checkout_state})
    assert len(mapping) == 114 and sum(r['bytes'] for r in mapping) == contract['total_input_bytes']
    status = {'commit': contract['source_commit'], 'verified_count': len(mapping),
              'verified_bytes': contract['total_input_bytes'], 'unknown': [], 'retained_pack': str(pack),
              'pack_sha256': contract['pack']['sha256'], 'portable_manifest_sha256': sha256_file(contract_path),
              'scope': 'Exact historical bounded inputs only. No engine run, current-branch acceptance, or candidate adoption.'}
    write_exact(out / 'source_map.json', (json.dumps(mapping, indent=2) + '\n').encode())
    write_exact(out / 'closure_status.json', (json.dumps(status, indent=2) + '\n').encode())
    write_exact(out / 'preparation_receipt.json', (json.dumps({'repo': str(repo), 'choices': choices, **status}, indent=2) + '\n').encode())
    print(json.dumps({'prepared': str(out), 'inputs': len(mapping), 'source_commit': contract['source_commit'],
                      'checkout_matches': sum(x['source_kind'] == 'supplied_checkout' for x in choices),
                      'runtime_executed': False}))

if __name__ == '__main__':
    main()
