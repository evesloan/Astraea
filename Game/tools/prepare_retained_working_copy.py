"""Materialize only missing, hash-verified retained files in a separate checkout.
Never overwrites an existing file; --check-only performs no writes. No network.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-only', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
manifest = root / 'Game/docs/validation/panoramic_residential_integration_20261022/RECOVERED_ADDITIONS.json'
rows = json.loads(manifest.read_text())
verified = restored = 0
for row in rows:
    target = root / row['path']
    assert target.resolve().is_relative_to(root), 'Target escaped checkout'
    if target.exists():
        data = target.read_bytes()
    elif args.check_only:
        raise SystemExit('Missing retained working-copy file: ' + row['path'])
    elif 'archive' in row:
        with zipfile.ZipFile(root / row['archive']) as archive:
            data = archive.read(row['member'])
    else:
        data = (root / row['retained_path']).read_bytes()
    assert len(data) == row['bytes'], 'Size mismatch: ' + row['path']
    assert hashlib.sha256(data).hexdigest() == row['sha256'], 'Hash mismatch; preserving existing file: ' + row['path']
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as output:
            output.write(data)
        restored += 1
    verified += 1
print(json.dumps({'verified_files': verified, 'restored_missing_files': restored,
                  'existing_files_overwritten': 0, 'network_used': False}))
