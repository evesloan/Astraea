"""Recover exact retained source bytes; never rebuild or replace an original.

Run once in this isolated checkout. Archives remain independently retained at
the pinned Group2 branch. Native originals are restored outside the runtime
tree, with exact hashes and an archive-member recovery address in the receipt.
"""
import argparse, hashlib, io, json, pathlib, subprocess, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
PACKAGE = pathlib.Path(__file__).resolve().parent
REF = 'ae925fbb839a48c44f82f999a0687727283d70a4'
PREFIX = 'external_packages/group2_luxury_20261009/C/'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def exact_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, f'Existing bytes differ: {path}'
    else:
        path.write_bytes(data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', type=pathlib.Path, required=True)
    parser.add_argument('--receipt-root', type=pathlib.Path,
                        help='Optional new receipt directory for recovery in another checkout')
    parser.add_argument('--only', type=str)
    args = parser.parse_args()
    receipt_root = args.receipt_root or PACKAGE / 'evidence'
    receipt_root.mkdir(parents=True, exist_ok=True)
    index = json.loads((PACKAGE / 'prior_handoff/DELIVERY_INDEX.json').read_text())
    entries = index['luxury_sources'] + index['private_house_adjuncts']
    rows = []
    for i, entry in enumerate(entries):
        key = str(entry.get('unit_source_index', entry.get('house')))
        if args.only and key != args.only:
            continue
        receipt_path = receipt_root / f'recovery_{key}.json'
        if receipt_path.exists():
            previous = json.loads(receipt_path.read_text())
            if previous['all_pinned_archive_members_rehashed'] > 0:
                # A retained receipt alone does not restore its local files.
                # Check all existing bytes, and recover any missing outputs.
                assert previous['source_ref'] == REF
                checks = [(args.native_root / entry['original_native_path'], entry['native_sha256']),
                          (ROOT / previous['runtime_path'], entry['export_sha256']),
                          (ROOT / 'Game/data/group2_completion/contracts' / f'{key}.json', previous['contract_sha256'])]
                checks += [(ROOT / row['path'], row['sha256']) for row in previous['retained_evidence']]
                complete = True
                for path, expected in checks:
                    if path.exists():
                        assert sha(path.read_bytes()) == expected, f'Existing bytes differ: {path}'
                    else:
                        complete = False
                if complete:
                    rows.append(previous)
                    print(f'RETAINED_AND_REHASHED {i+1}/86 {key}', flush=True)
                    continue
            else:
                exact_write(receipt_root / f'recovery_{key}_INITIAL_CLOSURE_FIELD_OMISSION.json', receipt_path.read_bytes())
        data = subprocess.check_output(['git', 'show', f'{REF}:{PREFIX}{entry["archive_path"]}'], cwd=ROOT)
        assert len(data) == entry['archive_bytes'] and sha(data) == entry['archive_sha256']
        z = zipfile.ZipFile(io.BytesIO(data))
        names = z.namelist()
        def member(path):
            matches = [n for n in names if n.endswith('/' + path)]
            assert len(matches) == 1, (key, path, matches)
            return z.read(matches[0])
        manifest = json.loads(member(entry['manifest_path']))
        closure = manifest.get('pinned_dependency_closure', manifest.get('closure', []))
        assert closure, f'No dependency closure declared: {key}'
        for pin in closure:
            b = member(pin['path'])
            assert len(b) == pin['bytes'] and sha(b) == pin['sha256'], (key, pin['path'])
        native = member(entry['original_native_path'])
        export = member(entry['original_export_path'])
        assert sha(native) == entry['native_sha256'] and sha(export) == entry['export_sha256']
        native_path = args.native_root / entry['original_native_path']
        exact_write(native_path, native)
        runtime = ROOT / 'Game/assets/group2_completion' / f'{key}.glb'
        exact_write(runtime, export)
        contract_bytes = member(entry['contract_path'])
        contract = json.loads(contract_bytes)
        exact_write(ROOT / 'Game/data/group2_completion/contracts' / f'{key}.json', contract_bytes)
        section_prefix = entry['contract_path'].rsplit('/', 1)[0] + '/'
        section_files = []
        for n in names:
            rel = n.split('/', 1)[1]
            if rel.startswith(section_prefix) and not rel.endswith(('.blend', '.glb')):
                b = z.read(n)
                dest = PACKAGE / 'retained_evidence' / key / pathlib.Path(rel).name
                exact_write(dest, b)
                section_files.append({'path': str(dest.relative_to(ROOT)), 'bytes': len(b), 'sha256': sha(b)})
        row = {'key': key, 'source_ref': REF, 'archive_path': PREFIX + entry['archive_path'],
               'archive_bytes': len(data), 'archive_sha256': sha(data),
               'all_pinned_archive_members_rehashed': len(closure),
               'native_member': entry['original_native_path'], 'native_sha256': sha(native),
               'native_local': str(native_path), 'runtime_path': str(runtime.relative_to(ROOT)),
               'runtime_sha256': sha(export), 'contract_sha256': sha(contract_bytes),
               'retained_evidence': section_files, 'new_units': 0, 'installed_acceptance': False}
        receipt_path.write_text(json.dumps(row, indent=2) + '\n')
        rows.append(row)
        print(f'VERIFIED {i+1}/86 {key} closure={len(closure)} native={len(native)} runtime={len(export)}', flush=True)
    if not args.only:
        assert len(rows) == 86
        (receipt_root / 'RECOVERY_ALL86.json').write_text(json.dumps({'source_ref': REF, 'entries': rows, 'count': 86, 'pass': True}, indent=2) + '\n')

if __name__ == '__main__':
    main()
