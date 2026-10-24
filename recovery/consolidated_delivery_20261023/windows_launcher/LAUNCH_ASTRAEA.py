#!/usr/bin/env python3
"""Offline launcher for the immutable 1091d34e PCK and retained official editor.

No engine download, install, source import, permission change or source overwrite.
The official editor supports --main-pack; an old exported game EXE is not a substitute.
"""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

PCK = {
    'name': 'Astraea-1091d34e.pck',
    'bytes': 7314424115,
    'sha256': '2d1147008d4e91e7d4620bd91a3f3cd93da38117e5ac73151e8739b959d698d7',
}
ENGINE = {
    'name': 'Godot_v4.6.3-stable_win64.exe',
    'bytes': 172409864,
    'sha256': 'ef90e929ba1a6a4322860285d97f40f4aa349c90329a91b0e8b55b8df0f4cb00',
}


def verify(path, record):
    path = Path(path).resolve(strict=True)
    if not path.is_file() or path.stat().st_size != record['bytes']:
        raise ValueError('Wrong file or byte count: ' + str(path))
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != record['sha256']:
        raise ValueError('Exact file checksum differs: ' + str(path))
    return path


def main(argv=None):
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, default=base/'engine'/ENGINE['name'])
    parser.add_argument('--pck', type=Path, default=base/PCK['name'])
    parser.add_argument('--check-only', action='store_true')
    options = parser.parse_args(argv)
    try:
        engine = verify(options.engine, ENGINE)
        package = verify(options.pck, PCK)
    except (OSError, ValueError) as error:
        print('REFUSED:', error, file=sys.stderr)
        return 2
    print('Verified official Godot4.6.3 editor and exact1091d34e package.')
    print('Unfinished construction test: Windows playability, walking stability and60FPS are not accepted.')
    if options.check_only:
        return 0
    if sys.platform != 'win32':
        print('REFUSED: native Windows launch requires Windows; no emulator is started.', file=sys.stderr)
        return 2
    return subprocess.call([str(engine), '--main-pack', str(package)], cwd=package.parent)


if __name__ == '__main__':
    raise SystemExit(main())
