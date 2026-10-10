"""Publish preserved own-source deliveries on the existing authorized branch only."""
import datetime, hashlib, json, os, pathlib, subprocess

R = pathlib.Path(__file__).resolve().parent
REPO = R / 'read_repository'
VERIFY = R / 'remote_verification'
URL = 'https://github.com/evesloan/Astraea.git'
BRANCH = 'handoff/group2-luxury-c-20261009'
PREFIX = 'external_packages/group2_luxury_20261009/C/'
RECEIPT = R / 'COMPLETE_HANDOFF_REMOTE_RECEIPT.json'

def git(args, cwd=REPO, data=None):
    p = subprocess.run(['git', *args], cwd=cwd, input=data, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout.decode().strip()

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def head():
    local = git(['rev-parse', 'refs/heads/' + BRANCH])
    remote = git(['ls-remote', URL, 'refs/heads/' + BRANCH]).split()[0]
    assert local == remote, 'Own handoff branch changed externally; preserve and stop'
    return local

def publish(files, label):
    parent = head()
    git(['read-tree', parent])
    targets = []
    for file in files:
        assert file.is_relative_to(R) and file.is_file()
        path = PREFIX + file.relative_to(R).as_posix()
        oid = git(['hash-object', '--no-filters', '-w', str(file)])
        git(['update-index', '--add', '--cacheinfo', '100644', oid, path])
        targets.append(dict(path=path, git_blob=oid, bytes=file.stat().st_size, sha256=sha(file)))
    tree = git(['write-tree', '--missing-ok'])
    if tree == git(['rev-parse', parent + '^{tree}']):
        commit = parent
    else:
        commit = git(['commit-tree', tree, '-p', parent], data=(label + '\n').encode())
        changed = git(['diff-tree', '--no-commit-id', '--name-only', '-r', parent, commit]).splitlines()
        assert set(changed) <= {t['path'] for t in targets}
        # Push before changing the local branch so a failed push preserves agreement.
        git(['push', URL, commit + ':refs/heads/' + BRANCH])
        git(['update-ref', 'refs/heads/' + BRANCH, commit, parent])
    assert git(['ls-remote', URL, 'refs/heads/' + BRANCH]).split()[0] == commit
    print('PUSHED', label, commit, flush=True)
    git(['fetch', '--depth=1', '--filter=blob:none', URL, 'refs/heads/' + BRANCH], cwd=VERIFY)
    assert git(['rev-parse', 'FETCH_HEAD'], cwd=VERIFY) == commit
    tree_entries = git(['ls-tree', '-r', commit, '--', PREFIX], cwd=VERIFY)
    mapping = {line.split('\t', 1)[1]: line.split()[2] for line in tree_entries.splitlines()}
    for t in targets:
        assert mapping[t['path']] == t['git_blob']
    # Fetch missing blobs in one remote operation, never copy the publisher's objects.
    present = set(git(['cat-file', '--batch-all-objects', '--batch-check=%(objectname)'], cwd=VERIFY).splitlines())
    missing = sorted({t['git_blob'] for t in targets} - present)
    if missing:
        git(['fetch', '--no-tags', URL, *missing], cwd=VERIFY)
    for t in targets:
        h = hashlib.sha256(); count = 0
        p = subprocess.Popen(['git', 'cat-file', 'blob', t['git_blob']], cwd=VERIFY, stdout=subprocess.PIPE)
        while True:
            b = p.stdout.read(4 * 1024 * 1024)
            if not b: break
            h.update(b); count += len(b)
        assert p.wait() == 0 and count == t['bytes'] and h.hexdigest() == t['sha256'], t['path']
    print('REMOTE_HASH_VERIFIED', len(targets), commit, flush=True)
    return dict(commit=commit, files=targets, independent_remote_download=True,
                verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())

def main():
    index = json.loads((R / 'DELIVERY_INDEX.json').read_text())
    entries = index['luxury_sources'] + index['private_house_adjuncts']
    archives = sorted((R / 'deliveries').glob('*.zip'))
    assert len(entries) == 86 and len(archives) == 96
    for e in entries:
        p = R / e['archive_path']
        assert p.stat().st_size == e['archive_bytes'] and sha(p) == e['archive_sha256']
    pending = []
    for p in archives:
        summary = p.with_suffix('.json')
        assert json.loads(summary.read_text())['archive_sha256'] == sha(p)
        receipt = R / (p.stem + '_REMOTE_RECEIPT.json')
        if receipt.exists():
            old = json.loads(receipt.read_text())
            if any(t['path'] == PREFIX + 'deliveries/' + p.name and t['sha256'] == sha(p) for t in old['files']):
                continue
        pending.append(p)
    print('PRESERVED_ARCHIVES', len(archives), 'PENDING', len(pending), flush=True)
    report = dict(branch=BRANCH, repository=URL, current_archives=86,
                  current_archive_bytes=sum(e['archive_bytes'] for e in entries),
                  historical_superseded_archives=10, main_written=False,
                  credentials_changed=False, source_construction_performed=False, milestones=[])
    if RECEIPT.exists():
        report['milestones'] = json.loads(RECEIPT.read_text()).get('milestones', [])
    for start in range(0, len(pending), 8):
        group = pending[start:start+8]
        files = [f for p in group for f in (p, p.with_suffix('.json'))]
        m = publish(files, 'Group2 C retained source archives ' + str(start + 1) + '-' + str(start + len(group)))
        report['milestones'].append(m)
        RECEIPT.write_text(json.dumps(report, indent=2))
        for archive in group:
            pair = [t for t in m['files'] if t['path'] in {PREFIX + 'deliveries/' + archive.name, PREFIX + 'deliveries/' + archive.with_suffix('.json').name}]
            receipt = dict(branch=BRANCH, commit=m['commit'], independent_fresh_remote_download=True,
                           files=pair, verified_utc=m['verified_utc'], main_written=False,
                           credentials_changed=False, shared_live_registry_changed=False)
            (R / (archive.stem + '_REMOTE_RECEIPT.json')).write_text(json.dumps(receipt, indent=2))
    # Retain source recipes, pins, blockers, manifests and receipts alongside archives.
    metadata = sorted(p for p in R.iterdir() if p.is_file() and p.suffix in {'.py', '.json', '.md'} and p != RECEIPT)
    m = publish(metadata, 'Group2 C complete source handoff index and retained provenance')
    report['milestones'].append(m)
    # Check every final archive blob against the final remote tree and independent downloaded bytes.
    all_files = [f for p in archives for f in (p, p.with_suffix('.json'))]
    m = publish(all_files, 'Group2 C complete preserved archive verification')
    report['milestones'].append(m)
    report['complete_remote_hash_verification'] = True
    report['archive_count_including_superseded'] = len(archives)
    report['all_archive_bytes_including_superseded'] = sum(p.stat().st_size for p in archives)
    report['final_verified_archive_commit'] = m['commit']
    RECEIPT.write_text(json.dumps(report, indent=2))
    final = publish([RECEIPT], 'Group2 C complete remote retention receipt')
    print('COMPLETE_HANDOFF', final['commit'], 'CURRENT86', report['current_archive_bytes'], 'PRESERVED96', report['all_archive_bytes_including_superseded'], flush=True)

if __name__ == '__main__':
    main()
