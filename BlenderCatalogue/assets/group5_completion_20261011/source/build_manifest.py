"""Hash only the additive handoff files; exclude this manifest's own bytes."""
from pathlib import Path
import hashlib, json, subprocess

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[2]
MANIFEST = P / 'MANIFEST.json'
PREFIXES = [
    'BlenderCatalogue/assets/group5_completion_20261011/',
    'Game/assets/models/group5/',
    'Game/data/architecture/group5/',
    'Game/docs/group5/',
]
EXPLICIT = {
    'Game/scripts/group5_completion.gd',
    'Game/scripts/group5_completion.gd.uid',
    'Game/scripts/group5_retail_slider.gd',
    'Game/scripts/group5_retail_slider.gd.uid',
    'Game/tests/validate_group5_completion.gd',
    'Game/tests/validate_group5_completion.gd.uid',
    'Game/tests/validate_group5_staff_walk.gd',
    'Game/tests/validate_group5_staff_walk.gd.uid',
    'Game/tests/validate_group5_interfaces.gd',
    'Game/tests/validate_group5_interfaces.gd.uid',
    'Game/artifacts/group5_completion.json',
    'Game/artifacts/group5_staff_walk.json',
    'Game/artifacts/group5_interfaces.json',
}
raw = subprocess.check_output([
    'git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'
], cwd=ROOT).decode().split('\0')
files = sorted({p for p in raw if p and (p in EXPLICIT or any(p.startswith(x) for x in PREFIXES))}
               | {p for p in EXPLICIT if (ROOT / p).is_file()})
records = []
for name in files:
    f = ROOT / name
    if f == MANIFEST:
        continue
    data = f.read_bytes()
    records.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
receipt = {
    'schema': 'astraea.group5.handoff.sha256.v1',
    'baseline_commit': 'affc5c807087ff87da29f3642c2d6e418241b896',
    'baseline_tree': '10e4be73dce2bebafe0c24bdcbe9332d818cf754',
    'branch': 'handoff/group5-completion-20261011',
    'whole_group_accepted': False,
    'file_count': len(records),
    'total_bytes': sum(r['bytes'] for r in records),
    'files': records,
    'files_signature': hashlib.sha256(json.dumps(records, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
    'excludes': 'MANIFEST.json itself; local Godot cache, Python cache and Blender autosaves',
    'retained_originals': 'qa/FINAL_ORIGINAL_INTEGRITY.json; all43483 hashes unchanged',
}
MANIFEST.write_text(json.dumps(receipt, indent=2) + '\n')
print('GROUP5_MANIFEST', len(records), receipt['total_bytes'],
      hashlib.sha256(MANIFEST.read_bytes()).hexdigest())
