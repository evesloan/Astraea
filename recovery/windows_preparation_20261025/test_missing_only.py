"""Exercise the real publication path on disposable files, without an engine."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile

repo = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('prepare_editor', repo / 'PREPARE_EDITOR.py')
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)
with tempfile.TemporaryDirectory(prefix='astraea-publish-test-') as directory:
    root = Path(directory)
    stage = root / 'stage'
    stage.mkdir()
    source = stage / 'source'
    source.write_bytes(b'retained bytes')
    row = {'path': 'out/input.bin', 'bytes': source.stat().st_size,
           'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    recipes = {row['path']: row}
    staged = {row['path']: source}
    assert prep.create_missing(root, recipes, staged, stage) == 1
    assert prep.create_missing(root, recipes, staged, stage) == 0
    survivor = root / row['path']
    survivor.write_bytes(b'unique survivor')
    try:
        prep.create_missing(root, recipes, staged, stage)
    except prep.Refused:
        pass
    else:
        raise AssertionError('Mismatched survivor was not refused')
    assert survivor.read_bytes() == b'unique survivor'
print('PASS: writable flush, atomic missing-only creation, idempotence, conflict preservation')
