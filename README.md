# Astraea editable construction handoff

Use branch `construction/group1-tidal-d15-20261010`. `main` is an older retained fallback, not the current handoff. Clone into a new directory; never overwrite an existing working copy.

## Prepare before opening Godot

With Godot closed, run from the checkout root:

```text
python PREPARE_EDITOR.py
python PREPARE_EDITOR.py --check-only
```

Python 3.9+ and a filesystem supporting local hard links are required (normal NTFS, APFS and Linux filesystems support them). Preparation is offline, uses only retained repository inputs, and creates at most 3,150 supplement files plus 11 runtime/native files. Allow at least 400 MB of temporary/final space. It verifies the exact 17,697-entry manifest and all 80 canonical repair files, then verifies every surviving required file before creating any target. Existing edits are conflicts, never overwritten. Each created file is independently editable; deduplicated PNGs are not linked together.

This is first-time, pinned-source setup, not a repair tool for later development edits. After intentional source edits, these pinned checks may fail; preserve those edits and review their contracts separately. This helper never regenerates contracts or refreshes guards. No general contract-regeneration command has been verified for this handoff.

Use only this entry point, not the historical layer installers. It does not change code, the manifest, main scene, feature flags or native source choices. A nonzero exit means stop and resolve the listed conflict or missing dependency in a separate copy. Do not delete an edited file simply to silence a conflict. An interrupted run can be repeated; completed files remain intact. If an interruption leaves `.astraea-prepare-editor.lock`, confirm no preparer is running before removing only that lock directory. `--check-only` writes nothing. Successful output is a source-preparation receipt, not a runtime acceptance result.

After `SOURCE_PREPARATION_PASS`, use Godot `4.6.3.stable.official.7d41c59c4`, Compatibility renderer, to open `Game/project.godot`. Its selected main remains `res://scenes/bootstrap_tram_section_integrated_20261024.tscn`. Automatic Blender import remains disabled. Keep one import/build owner at a time.

## What is and is not verified

Canonical Game source incorporates the Quiet/Family and release-operation delivery repairs plus the reviewed weak-reference texture repair. The private contact single-pass successor removes only a discarded initial contact build after final geometry/material/contact equivalence checks. Later queue, staged-activation and prewarm experiments remain held and are not selected defaults. The preparer was tested on all 3,161 exact target files, including interruption, idempotence and conflict refusal. The complete existing checkout passed preparation and the consolidated editor import with no logged errors or warnings. The frozen 1091d34e main passed a Linux headless startup; later source has the separately qualified evidence below. Full native/visual closure, Windows release assembly, walking stability and target-hardware performance remain separate gates. Earlier incomplete review-copy omissions are not current missing source.

A test PCK was exported from `1091d34e` and passed its packaged-byte checks. That source revision reached actual readiness in a bounded Linux headless run, including menu/settings persistence and Resume/pause. The later selected Tidal court/arrival source has focused integration checks only; it is not included in that immutable PCK and has not had a full startup run. There is **no verified current Windows playable delivery**; no Windows executable is included in this cloud package. The earlier Windows delivery had a walking crash; focused texture-ownership evidence does not establish that crash's cause or resolution. No 60 FPS or final visual/gameplay acceptance is claimed. `SOURCE_BUILD_STATUS.json` records the source/build boundary. Future deliveries must identify an exact source commit/tag and EXE/PCK hashes; older binaries are retained history, not current builds.

## Continue from the retained sources

- `Game/`: editable Godot scenes, scripts, runtime inputs and validation receipts.
- `BlenderCatalogue/`: native authoring assets and successors. Recent sources use Blender 4.3.2; retain historical version exceptions.
- `RetainedConstruction/`, `external_packages/`, `recovery/`, `DesignArchive/`: original packages, backups, references and history. Preserve all of them. `SOURCE_ARCHIVE_INDEX.json` is a historical archive map, not a complete index of later additions.
- `Game/docs/master_source/` and `Game/docs/WHOLE_SHIP_SECTION_COORDINATION.md`: architecture-first master and coordination requirements. Preserve room identities, allocations, deck datums and actual support/route ownership.
- `Game/docs/CURRENT_STATUS.md`: detailed unfinished construction and acceptance limits.

## Current integrated source boundary

The five-level Tidal arrival successor follows the court finish after the Tidal D14 landing and complete retained Star Atlas living construction chain. Its connected receiving and source-contract evidence is in `Game/tidal_court_finish_20261023/evidence`; the earlier landing geometry remains in `Game/tidal_d14_landing_20261023/evidence`. The earlier Windows executable remains a separate historical build. See `SOURCE_MAP.md` for human-readable ownership and entry points; keep unaccepted experiments and source candidates separate. Source preparation verifies bytes, not full gameplay or performance acceptance.

Final export-log review found ten editor dialog-ownership errors despite exit0; packaged-byte checks passed, but full exported-runtime acceptance remains open. See `recovery/consolidated_delivery_20261023/EXPORT_DIAGNOSTICS.json` and `LATE_VALIDATION_NOTES.md`.

The selected five-level Tidal court finish is a later source successor:267 existing opaque surfaces and16 retained physical emitter connections, with no added geometry or capacity. Its bounded view remains dark/plain and visually unaccepted. The frozen1091d34e PCK does not contain this later source finish. See Game/tidal_court_finish_20261023/README.md.

The D13–D17 arrival successor adds80 editable profiled crown parts,20 spatial/material batches and10 physical fixture lights.398 connected checks and8 detached launch scenes pass; all17576 exact source contracts verify. It also supplies the previously missing court ship-scene resource. The new contextual view remains unfinished. See [r002 package](Game/tidal_arrival_finish_20261024/README_r002.md).

## Current static tram integration

The selected entry now includes the neighbor-cleared tram section at X47.5, the unchanged curved CENTRAL docking/extended bridge, and all preceding Tidal/district construction. It preserves the original player, cart, products, controls, menus and settings. Boarding, joint locking and motion remain explicitly disabled. No new passenger or stop is invented.

The actual installed-world headless gate passed 25 connection checks and 583,837 contact queries across 211 components with zero hits. It reached readiness and deferred receiving completion, but its standalone test host omitted the normal World360 listener context and logged one audio-calibration error. This is contact/integration evidence, not a clean normal-presentation or playable release pass. The retained normal presentation is unchanged except its selected ship path. Eight detached scenes and 188 literal entry references resolve; 17,697 exact source contracts verify. See [selected tram evidence](recovery/tram_section_successor_20261024/root_r003/STATE.md).

The current source is newer than the 1091d34e PCK. Windows assembly remains unfinished: the normal shell read of the existing private release returned Forbidden, no executable was downloaded and that route was stopped. No credential/permission changes or alternate-route bypass occurred. Source publication remains available. All eight groups, moving tram/scenic performance, final art/gameplay, external StarAtlas r002 and unrecovered October20 WIP/tram intro remain open.
