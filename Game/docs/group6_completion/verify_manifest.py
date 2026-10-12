"""Verify the complete scoped handoff locally or from an independent Git clone."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--git-dir")
parser.add_argument("--revision", default="HEAD")
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]

def read(path):
    if args.git_dir:
        return subprocess.check_output(
            ["git", "--git-dir", args.git_dir, "show", args.revision + ":" + path]
        )
    return (root / path).read_bytes()

manifest_path = "Game/docs/group6_completion/COMPACT_MANIFEST.json"
manifest_bytes = read(manifest_path)
manifest = json.loads(manifest_bytes)
records = manifest["files"]
canonical = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
assert hashlib.sha256(canonical).hexdigest() == manifest["records_sha256"]
assert len(records) == manifest["file_count"]
assert sum(item["bytes"] for item in records) == manifest["total_bytes"]
failures = []
for item in records:
    data = read(item["path"])
    if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
        failures.append(item["path"])
for path, digest in manifest["protected_original_sha256"].items():
    if hashlib.sha256(read(path)).hexdigest() != digest:
        failures.append("protected original: " + path)
result = {
    "status": "PASS" if not failures else "HOLD",
    "files_checked": len(records),
    "bytes_checked": manifest["total_bytes"],
    "protected_originals_checked": len(manifest["protected_original_sha256"]),
    "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    "records_sha256": manifest["records_sha256"],
    "failures": failures,
    "independent_git_dir": args.git_dir,
}
if args.git_dir:
    for key, suffix in [("commit", ""), ("tree", "^{tree}")]:
        result[key] = subprocess.check_output(
            ["git", "--git-dir", args.git_dir, "rev-parse", args.revision + suffix], text=True
        ).strip()
print(json.dumps(result, indent=2))
if failures:
    raise SystemExit(1)
