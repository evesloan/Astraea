"""Verify offline Git restoration and independent family source ZIPs.

No Blender asset generators, project code or network operations are executed.
The result receipt is written outside the source repository by the caller.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, subprocess, tempfile, zipfile


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archives", nargs="+", type=Path, help="Oldest complete history, then incremental archives in order")
    ap.add_argument("--source-directory", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if args.report.exists():
        raise SystemExit("Preserve the existing receipt and choose another path")
    restored = []
    packages = []
    with tempfile.TemporaryDirectory(prefix="astraea-verified-restore-") as tmp:
        temp = Path(tmp)
        repo = temp / "repository"
        for index, path in enumerate(args.archives):
            with zipfile.ZipFile(path) as z:
                assert z.testzip() is None
                names = [n for n in z.namelist() if n.endswith("/BACKUP_MANIFEST.json")]
                assert len(names) == 1
                prefix = names[0].rsplit("/", 1)[0] + "/"
                manifest = json.loads(z.read(names[0]))
                history = z.read(prefix + "source-history.bundle")
                assert sha(history) == manifest["source_history"]["sha256"]
                bundle = temp / ("history_%02d.bundle" % index)
                bundle.write_bytes(history)
                if index == 0:
                    assert manifest["source_history"]["kind"] == "complete"
                    subprocess.run(["git", "clone", str(bundle), str(repo)], check=True, capture_output=True)
                else:
                    subprocess.run(["git", "-C", str(repo), "bundle", "verify", str(bundle)], check=True, capture_output=True)
                    subprocess.run(["git", "-C", str(repo), "fetch", str(bundle), "HEAD"], check=True, capture_output=True)
                subprocess.run(["git", "-C", str(repo), "checkout", "--detach", manifest["git_commit"]], check=True, capture_output=True)
                expected = {r["path"] for r in manifest["files"]}
                actual = set(subprocess.check_output(["git", "-C", str(repo), "ls-files", "-z"]).decode().strip("\0").split("\0"))
                assert actual == expected
                for row in manifest["files"]:
                    raw = (repo / row["path"]).read_bytes()
                    assert sha(raw) == row["sha256"] == sha(z.read(prefix + row["path"]))
                restored.append({"archive": str(path), "archive_sha256": sha(path.read_bytes()), "commit": manifest["git_commit"], "files_match": len(expected)})
        if args.source_directory:
            common = {}
            supplied = set()
            for path in sorted(args.source_directory.glob("*_Source_*.zip")):
                with zipfile.ZipFile(path) as z:
                    assert z.testzip() is None
                    checks = json.loads(z.read("PACKAGE_CHECKSUMS.json"))
                    for row in checks:
                        rel = PurePosixPath(row["path"])
                        assert not rel.is_absolute() and ".." not in rel.parts
                        raw = z.read(row["path"])
                        assert sha(raw) == row["sha256"] and len(raw) == row["bytes"]
                        if row["path"] in common:
                            assert common[row["path"]] == sha(raw), "Shared file differs across packages"
                        common[row["path"]] = sha(raw)
                    family_names = [n for n in z.namelist() if "/FAMILY_CONTENTS_" in n]
                    assert len(family_names) == 1
                    family = json.loads(z.read(family_names[0]))
                    catalog = json.loads(z.read("Astraea_Catalogue/catalogue_manifest.json"))
                    ids = set(family["unique_authored_asset_ids"])
                    assert not supplied.intersection(ids)
                    for asset in catalog["assets"]:
                        if asset["catalogue_id"] not in ids:
                            continue
                        for kind in ("source", "export"):
                            assert sha(z.read("Astraea_Catalogue/" + asset[kind])) == asset[kind + "_sha256"]
                        assert "Astraea_Catalogue/" + asset["manifest"] in z.namelist()
                    supplied.update(ids)
                    packages.append({"archive": str(path), "sha256": sha(path.read_bytes()), "family": family["family"], "assets": len(ids), "verified_files": len(checks)})
            assert packages
            assert supplied == {a["catalogue_id"] for a in catalog["assets"]}
            source_rows = [r for r in manifest["files"] if "/qa/" not in "/" + r["path"] and not r["path"].startswith("references/")]
            for row in source_rows:
                assert common["Astraea_Catalogue/" + row["path"]] == row["sha256"]
    report = {"passed": True, "scope": "Offline portable-history restore and complete family-source byte/dependency verification; no source code execution", "history_chain": restored, "source_packages": packages, "network_used": False}
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
