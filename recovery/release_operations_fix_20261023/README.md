# Release operations repair — validation pending

This is an additive delivery overlay for frozen f94cc1c8 plus the cumulative 854dc6db Quiet/Family fix. It does not modify the frozen source checkout or include the optional D04 optimization candidate. Preserve the known editor-tested baseline and its exported files.

Required GLTF/config/hash operations previously inside assert now execute in both debug and release. Explicit error paths stop the SceneTree with exit code 2. Night Garden obtains its receiving replacement before removing four predecessor walls. D17 validates both imported/raw scene branches and all replacement preimages, contacts and unchanged bounds before any owner mutation. No geometry, tolerance, room identity, capacity or material edits are included.

The reported release access violation has NOT been fully symbolicated. D17's ordinary main call uses its imported scene, whereas its assert-wrapped GLTF call belongs to the optional raw branch. The repair addresses proven release omissions and adds bounded fail-safe diagnostics; it is not proof that every crash cause is fixed.

## Install only after coordinated approval

Run `python apply.py --repo PATH` for a complete preimage/payload check. `--apply` backs up exact replaced bytes under `.astraea-delivery-backups/release-operations-20261023`, refuses unknown preimages, and verifies all resulting hashes. It launches nothing. PATCH.json lists every exact changed-file SHA256 and accepted preimage; MANIFEST_DELTA.json records changes to the source-contract manifest. Preserve backups and earlier revisions.

## Focused release validation

Use the existing official Windows RELEASE executable, not the editor. No full ship export is necessary for this fixture. The probe pack contains the repair source and fixture only; it mounts the existing baseline ship PCK and then remounts itself to override changed source. Pass absolute paths:

`Astraea.exe --headless --main-pack release-operations-probe.pck --script res://release_fixture.gd -- --baseline=BASELINE.pck --overlay=release-operations-probe.pck --mode=operations`

The fixture first mounts the embedded `runtime_source_contracts.pck`, as the production bootstrap does, before the repair overlay. Run `--mode=d17` and `--mode=d17-raw` separately for the actual standard receiving / Royalty successor chain using exact retained fore frame and aft owner geometry. Unrelated fore care rooms are omitted. Run `--mode=chain` separately for the actual Quiet/Family receiving chain and FamilyMeal adapter. Each positive run must exit 0, log `debug=false`, and have no script errors/assertion failures. Editor execution requires explicit `--allow-editor=1` and is only preflight evidence.

Negative cases `--mode=negative-glb` and `--mode=negative-config` must exit 2 with `ASTRAEA_RELEASE_GUARD`, not crash, report readiness or proceed to construction. Do not run four tests concurrently. A full release startup/export remains owned by the laptop task and must be separately coordinated after focused results.

## Pin handling and retained history

Current path-bound dependency pins are updated transitively. Historical inverse_edits rollback hashes remain unchanged: these describe prior revisions, not current required input bytes. METADATA_VALIDATION.json confirms every changed JSON value outside the source manifest is an exact SHA256 substitution; geometry, identities and nonhash fields are unchanged. The manifest covers all overlay dependencies, including the new guard.

The rejected Night Garden gallery and standalone Royalty source candidate remain historical/unintegrated; editor utilities and diagnostic-only SceneTree scripts are outside actual startup. They were not silently adopted or rewritten.

No final playable, visual, physics or whole-ship performance acceptance is claimed by this repair.
