#!/usr/bin/env python3
"""Verify/restore the exact split ZIP without creating a joined ZIP copy."""
import argparse
import bisect
import hashlib
import io
import json
from pathlib import Path
import zipfile

class ConcatenatedParts(io.RawIOBase):
    def __init__(self, paths):
        self.paths = paths
        self.offsets = [0]
        for path in paths:
            self.offsets.append(self.offsets[-1] + path.stat().st_size)
        self.position = 0
        self.current = None
        self.file = None

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.position

    def seek(self, offset, whence=0):
        position = offset if whence == 0 else self.position + offset if whence == 1 else self.offsets[-1] + offset
        if position < 0:
            raise ValueError("Negative seek")
        self.position = position
        return position

    def read(self, size=-1):
        remaining = self.offsets[-1] - self.position
        size = remaining if size < 0 else min(size, remaining)
        result = bytearray()
        while size > 0:
            part = bisect.bisect_right(self.offsets, self.position) - 1
            if part != self.current:
                if self.file: self.file.close()
                self.file = self.paths[part].open("rb")
                self.current = part
            self.file.seek(self.position - self.offsets[part])
            amount = min(size, self.offsets[part + 1] - self.position)
            block = self.file.read(amount)
            if len(block) != amount:
                raise IOError("A verified part changed or became unreadable")
            result.extend(block)
            self.position += amount
            size -= amount
        return bytes(result)

    def close(self):
        if self.file: self.file.close()
        super().close()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).with_name("TRANSFER_MANIFEST.json"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not args.verify_only and args.output is None:
        parser.error("Choose a new --output directory or --verify-only")
    manifest = json.loads(args.manifest.read_text())
    archive_hash = hashlib.sha256()
    archive_bytes = 0
    paths = []
    for row in manifest["parts"]:
        if Path(row["name"]).name != row["name"]:
            raise ValueError("Unsafe part name")
        path = args.manifest.parent / row["name"]
        h = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            while block := stream.read(8 * 1024**2):
                h.update(block)
                archive_hash.update(block)
                size += len(block)
        if size != row["bytes"] or h.hexdigest() != row["sha256"]:
            raise ValueError("Part mismatch: " + row["name"])
        archive_bytes += size
        paths.append(path)
    if archive_bytes != manifest["archive"]["bytes"] or archive_hash.hexdigest() != manifest["archive"]["sha256"]:
        raise ValueError("Combined ZIP digest differs")
    artifact = manifest["artifact"]
    if Path(artifact["name"]).name != artifact["name"]:
        raise ValueError("Unsafe artifact name")
    target = None
    h = hashlib.sha256()
    size = 0
    with ConcatenatedParts(paths) as combined, zipfile.ZipFile(combined) as archive:
        infos = archive.infolist()
        if len(infos) != 1 or infos[0].filename != artifact["name"] or infos[0].file_size != artifact["bytes"]:
            raise ValueError("Unexpected ZIP contents")
        if not args.verify_only:
            args.output.mkdir(parents=True, exist_ok=False)
            target = args.output / artifact["name"]
        output = target.open("xb") if target else None
        try:
            with archive.open(infos[0]) as source:
                while block := source.read(8 * 1024**2):
                    h.update(block)
                    size += len(block)
                    if output: output.write(block)
        finally:
            if output: output.close()
    if size != artifact["bytes"] or h.hexdigest() != artifact["sha256"]:
        raise ValueError("Decoded PCK mismatch; do not launch")
    print(json.dumps({"status":"EXACT_TRANSPORT_PASS", "source_commit":manifest["source_commit"],
                      "pck_bytes":size, "pck_sha256":h.hexdigest(), "parts":len(paths),
                      "restored_to":str(target) if target else None, "playability_tested":False}))

if __name__ == "__main__":
    main()
