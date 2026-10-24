"""Bounded launcher safety/path checks. Does not execute Windows or a game."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('launcher', Path(__file__).with_name('LAUNCH_ASTRAEA.py'))
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)

with tempfile.TemporaryDirectory(prefix='astraea launcher check ') as directory:
    base = Path(directory)
    engine, package = base/'engine with spaces.exe', base/'package with spaces.pck'
    engine.write_bytes(b'fixture engine'); package.write_bytes(b'fixture package')
    record = lambda p: dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest(), name=p.name)
    args = ['--engine', str(engine), '--pck', str(package)]
    with patch.object(launcher, 'ENGINE', record(engine)), patch.object(launcher, 'PCK', record(package)), patch.object(launcher.subprocess, 'call', return_value=0) as execute:
        assert launcher.main(args+['--check-only']) == 0
        execute.assert_not_called()
        with patch.object(launcher.sys, 'platform', 'win32'):
            assert launcher.main(args) == 0
        execute.assert_called_once_with([str(engine), '--main-pack', str(package)], cwd=package.parent)
        execute.reset_mock()
        engine.write_bytes(b'fixture enginf')
        assert launcher.main(args) == 2
        execute.assert_not_called()
        assert package.read_bytes() == b'fixture package'
print('PASS: check-only, argument-safe paths, exact hash refusal, no package mutation; no native execution')
