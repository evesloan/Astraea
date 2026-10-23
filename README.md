# Astraea editable construction handoff

Use branch `construction/group1-tidal-d15-20261010`. `main` is an older retained fallback, not the current handoff. Clone into a new directory; never overwrite an existing working copy.

## Prepare before opening Godot

With Godot closed, run from the checkout root:

```text
python PREPARE_EDITOR.py
python PREPARE_EDITOR.py --check-only
```

Python 3.9+ and a filesystem supporting local hard links are required (normal NTFS, APFS and Linux filesystems support them). Preparation is offline, uses only retained repository inputs, and creates at most 3,150 supplement files plus 11 runtime/native files. Allow at least 400 MB of temporary/final space. It verifies the exact 17,566-entry manifest and all 80 canonical repair files, then verifies every surviving required file before creating any target. Existing edits are conflicts, never overwritten. Each created file is independently editable; deduplicated PNGs are not linked together.

This is first-time, pinned-source setup, not a repair tool for later development edits. After intentional source edits, these pinned checks may fail; preserve those edits and review their contracts separately. This helper never regenerates contracts or refreshes guards. No general contract-regeneration command has been verified for this handoff.

Use only this entry point, not the historical layer installers. It does not change code, the manifest, main scene, feature flags or native source choices. A nonzero exit means stop and resolve the listed conflict or missing dependency in a separate copy. Do not delete an edited file simply to silence a conflict. An interrupted run can be repeated; completed files remain intact. If an interruption leaves `.astraea-prepare-editor.lock`, confirm no preparer is running before removing only that lock directory. `--check-only` writes nothing. Successful output is a source-preparation receipt, not a runtime acceptance result.

After `SOURCE_PREPARATION_PASS`, use Godot `4.6.3.stable.official.7d41c59c4`, Compatibility renderer, to open `Game/project.godot`. Its selected main remains `res://scenes/bootstrap_star_atlas_living_20261022.tscn`. Automatic Blender import remains disabled. Keep one import/build owner at a time.

## What is and is not verified

Canonical Game source incorporates the Quiet/Family and release-operation delivery repairs plus the reviewed weak-reference texture repair. Later route, staged-activation and prewarm experiments remain held and are not selected defaults. The preparer was tested on all 3,161 exact target files, including interruption, idempotence and conflict refusal. A complete checkout preparation pass, editor import/startup, full native/runtime closure and a matching release build remain pending. The review workspace lacked 38 unchanged large Sunset SCNs that remain in Git; the helper correctly refuses incomplete copies rather than bypassing their hashes.

There is **no verified current matching playable build**. The earlier Windows delivery had a walking crash; focused texture-ownership evidence does not establish that crash's cause or resolution. No 60 FPS or final visual/gameplay acceptance is claimed. `SOURCE_BUILD_STATUS.json` records the source/build boundary. Future deliveries must identify an exact source commit/tag and EXE/PCK hashes; older binaries are retained history, not current builds.

## Continue from the retained sources

- `Game/`: editable Godot scenes, scripts, runtime inputs and validation receipts.
- `BlenderCatalogue/`: native authoring assets and successors. Recent sources use Blender 4.3.2; retain historical version exceptions.
- `RetainedConstruction/`, `external_packages/`, `recovery/`, `DesignArchive/`: original packages, backups, references and history. Preserve all of them. `SOURCE_ARCHIVE_INDEX.json` is a historical archive map, not a complete index of later additions.
- `Game/docs/master_source/` and `Game/docs/WHOLE_SHIP_SECTION_COORDINATION.md`: architecture-first master and coordination requirements. Preserve room identities, allocations, deck datums and actual support/route ownership.
- `Game/docs/CURRENT_STATUS.md`: detailed unfinished construction and acceptance limits.
