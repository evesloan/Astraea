"""Partition verified source bytes into independently usable family deliveries.

This code only packages bytes. It never executes asset generators or Git history.
"""
import json
from pathlib import PurePosixPath


def is_review_file(path):
    """Media and generated standalone package folders are evidence; texture and editable-source folders are not."""
    rel = PurePosixPath(path)
    return rel.parts[0] == 'references' or any(part in ('qa', 'renders', 'packages') for part in rel.parts[:-1])


def partition_sources(items, config, catalogue):
    prefix = "Astraea_Catalogue/"
    names = [name for name, _ in items]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate source path")
    ownership = {}
    for group in config["groups"]:
        name = group["name"]
        if not name or not all(c.isalnum() or c == "_" for c in name):
            raise ValueError("Unsafe family name")
        for folder in group["asset_directories"]:
            if folder in ownership:
                raise ValueError("Asset directory belongs to multiple families")
            ownership[folder] = name
    common = []
    selected = {g["name"]: [] for g in config["groups"]}
    for path, raw in items:
        if not path.startswith(prefix):
            raise ValueError("Source path outside catalogue")
        rel = PurePosixPath(path[len(prefix):])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Unsafe source path")
        if rel.parts[0] == "assets":
            if len(rel.parts) < 3 or rel.parts[1] not in ownership:
                raise ValueError("Unassigned asset source: " + str(rel))
            selected[ownership[rel.parts[1]]].append((path, raw))
        else:
            common.append((path, raw))
    result = []
    for group in config["groups"]:
        family = group["name"]
        if not selected[family]:
            continue
        payload = common + selected[family]
        available = {n[len(prefix):] for n, _ in payload}
        assets = [a for a in catalogue["assets"]
                  if PurePosixPath(a["source"]).parts[1] in group["asset_directories"]]
        for asset in assets:
            for key in ("source", "export", "manifest"):
                if asset[key] not in available:
                    raise ValueError(f"Missing {family} {key}: {asset[key]}")
        description = {
            "family": family,
            "unique_authored_asset_ids": [a["catalogue_id"] for a in assets],
            "source_asset_directories": group["asset_directories"],
            "scope": "Complete family source and exported components. No original game recovery or engine integration.",
            "shared_dependencies": "All common materials, standards and source tooling are included identically in each family ZIP.",
            "restoration": "Extract normally. To combine families, extract them into the same destination; common files have identical hashes. Source history and component QA are optional separate records.",
            "global_catalogue_index": "catalogue_manifest.json lists all families; only the IDs above are supplied in this family package.",
        }
        payload.append((prefix + "FAMILY_CONTENTS_" + family + ".json",
                        (json.dumps(description, indent=2) + "\n").encode()))
        result.append((family, payload, description))
    covered = {n for _, rows, _ in result for n, _ in rows if n in set(names)}
    if covered != set(names):
        raise ValueError("A source file was omitted from family deliveries")
    return result
