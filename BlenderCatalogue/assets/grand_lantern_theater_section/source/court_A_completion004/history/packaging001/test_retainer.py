"""Pure-file guarded-copier checks, exclusively in new scratch fixtures."""
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('retainer', HERE / 'retain_new_only.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
results = []


def case(kind):
    with tempfile.TemporaryDirectory(prefix='copier_test_', dir=HERE) as temp:
        root = Path(temp)
        m.TARGET = root / 'output'
        source = root / 'source.bin'
        source.write_bytes(b'new-only verified payload\x00\xff')
        protected = root / 'protected.bin'
        protected.write_bytes(b'original never changed')
        row = {'source': str(source), 'destination_relative': 'nested/source.bin',
               'destination': str(m.TARGET / 'nested/source.bin'), 'sha256': m.sha(source), 'bytes': source.stat().st_size}
        pin = {'source': str(protected), 'sha256': m.sha(protected), 'bytes': protected.stat().st_size}
        data = {'schema': 'astraea.court_a.source_retention.v1', 'target': str(m.TARGET),
                'files': [row], 'protected_inputs': [pin], 'payload_file_count': 1,
                'payload_bytes': row['bytes'], 'acceptance_limits': ['Source-only test fixture']}
        if kind == 'traversal':
            row['destination_relative'] = '../escape.bin'
            row['destination'] = str(m.TARGET / '../escape.bin')
        if kind == 'duplicate':
            data['files'].append(row.copy())
            data['payload_file_count'] = 2
            data['payload_bytes'] *= 2
        manifest = root / 'manifest.json'
        manifest.write_text(json.dumps(data))
        expected = m.sha(manifest)
        if kind == 'manifest_tamper':
            manifest.write_text(manifest.read_text() + ' ')
        if kind == 'source_tamper':
            source.write_bytes(b'changed')
        if kind == 'protected_tamper':
            protected.write_bytes(b'changed')
        if kind == 'existing_file':
            m.TARGET.write_bytes(b'surviving')
        if kind == 'existing_directory':
            m.TARGET.mkdir()
            (m.TARGET / 'surviving').write_bytes(b'keep')
        if kind == 'existing_symlink':
            m.TARGET.symlink_to(root / 'missing', target_is_directory=True)
        before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
        if kind == 'success':
            first = m.retain(manifest, expected)
            assert first['status'] == 'PASS_READ_ONLY_PREFLIGHT' and not m.TARGET.exists()
            result = m.retain(manifest, expected, True)
            assert result['status'] == 'PASS_NEW_ONLY_SOURCE_RETENTION'
            assert result['final_file_count'] == 3
            assert (m.TARGET / 'nested/source.bin').read_bytes() == source.read_bytes()
            assert m.sha(m.TARGET / m.MANIFEST_NAME) == expected
            assert protected.read_bytes() == b'original never changed'
            try:
                m.retain(manifest, expected, True)
            except RuntimeError:
                pass
            else:
                raise AssertionError('Repeated copy accepted')
            results.append({'case': 'valid_copy_and_repeat_refusal', 'passed': True})
        else:
            try:
                m.retain(manifest, expected, True)
            except (RuntimeError, FileExistsError):
                pass
            else:
                raise AssertionError('Unsafe case accepted: ' + kind)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
            assert before == after, 'Refusal changed files: ' + kind
            results.append({'case': kind, 'passed': True})


for kind in ['success', 'existing_file', 'existing_directory', 'existing_symlink', 'source_tamper', 'protected_tamper', 'manifest_tamper', 'traversal', 'duplicate']:
    case(kind)
result = {'status': 'PASS_PURE_FILE_COPIER_TESTS', 'cases': results,
          'production_paths_written': [], 'engines_or_git_started': False,
          'wrapper_sha256': m.sha(HERE / 'retain_new_only.py')}
with (HERE / 'COPIER_TEST_REPORT.json').open('x') as out:
    json.dump(result, out, indent=2)
    out.write('\n')
print(json.dumps(result))
