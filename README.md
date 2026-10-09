# Astraea current construction project

Open `Game/project.godot` with Godot 4.6.3 (Compatibility renderer). This is the current integrated ship project, not a finished game or final-art release.

## Current construction

All 23 destinations in the latest helper batch are installed, for 83 received section keys including the earlier 60. The 18 bulk installations use nearby-room loading; their structural floors remain present globally. The actual main scene boot and all 18 individual source asset hash/mesh/light checks pass. Detailed movement, cart/species fit, gameplay, furnishing and visual polish remain unfinished. See `Game/docs/CURRENT_STATUS.md` and `Game/docs/REMAINING_SECTION_INSTALLATIONS.json`.

## Where the editable sources are

- `Game/`: current runnable Godot source and runtime assets.
- `SOURCE_ARCHIVE_INDEX.json`: authoritative map of original helper packages, receiving corrections, retained native Blender sources and recovery order.
- `external_packages/`: exact original helper archives and current Equipment/Medical receiver derivatives. Recovered Cinema 1 and Long Library archives have ordered byte parts with checksums and reconstruction instructions.
- `BlenderCatalogue/`: retained unpacked baseline catalogue. Later native sources are in the indexed archives and checkpoint packages; this directory alone is not the complete current authoring set.
- `DesignArchive/`: retained references and historical plans. Current master v0.3 material is in `Game/docs/master_source/`.

Extract source archives into separate empty directories and verify their manifests before using them. Do not overlay historical Game files from checkpoint ZIPs onto current `Game/`. Files named `.zip.partNNN` require ordered concatenation. Cinema 5's two `PART_01_OF_02.zip` / `PART_02_OF_02.zip` archives are independent ZIPs and must not be concatenated.

## Simple branch workflow

`main` is the canonical current project. `checkpoint/direct-integration-20261009` is the single active integration/publication branch. The older source and helper branches are retained history, not additional working copies that need to be combined manually. Unique work has not been deleted.

`CHECKPOINT.json` records the current Game file inventory and retained source archive identities. `BACKUP_STATUS.json` is its compact summary. The former automatic watcher is not verified running in this cloud environment; protection currently uses published meaningful checkpoints. Do not infer continuous backup protection from branch activity alone.

## Scope of verification

The main-scene boot is a focused loading check, not a full-ship route or gameplay acceptance test. Nearby-room streaming was introduced after an eager all-interior load exited with code 137. Final rendering quality, interactions, target-hardware performance and complete ship construction remain open.

One large D12 directory editable Blender source is retained byte-for-byte in `external_packages/native_source_archives/D12_directory_08_native_exact.zip`, with its original path and hashes in `SOURCE_ARCHIVE_INDEX.json`. It is not a Godot runtime dependency. The unpacked Game tree has 10,070 files; this authoring file is additionally preserved in the ZIP.
