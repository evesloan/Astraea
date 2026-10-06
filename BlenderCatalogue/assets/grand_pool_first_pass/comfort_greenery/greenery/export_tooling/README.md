# Grand Pool greenery export reproducibility packet

Prepared in scratch for one new approved folder:

`assets/grand_pool_first_pass/comfort_greenery/greenery/export_tooling`

This packet contains byte-identical validated export tools, the unchanged strict keeper, r002 precision wrappers, the read-only diagnostic, immutable input records, independent source-retention evidence, historical logs/receipts, and 17 pure tests. Preparing it performed no shared-project write, Blender/engine job, backup operation, git operation or Game/runtime edit.

## Current status

- All 23 saved source files passed independent source QA and were independently retained as exact source bytes, separate retained files and committed blobs at verified remote commit `1b0e0061e3763539e364d0c53de4160f3a662f69`.
- All 23 r002 exports passed the original strict actual-GLB/source keeper: 77,258 triangles and 103 material-role batches. Maximum position deviation is zero, maximum UV deviation is 5.960464477539063e-8, and maximum normal deviation is 2.1696418193818683e-7. The original position/UV/normal limits remain 2e-6.
- The parent reports the checked source bundle is now installed as a Game candidate. That is separate from final visual acceptance. Current-world matched visual review, aesthetic refinement and related runtime work remain under the parent. This packet does not newly certify those outcomes or launch that work.

Historical receipt wording is preserved exactly, including earlier pending statuses and the failed first export. `PACKAGE_STATUS.json` is the current snapshot summary; it does not rewrite history.

## Why r002 exists

The official Blender 4.3.2 exporter rounded corner normals to four decimal places before renormalizing. The first strict equivalence run caught the resulting loss. The read-only diagnostic established exact exported positions and tiny UV rounding while normals exceeded the strict limit.

`precise_normal_export.py` temporarily sets that exporter process's normal rounding to eight decimal places and restores the original value in `finally`. It checks the installed extractor hash and baseline setting first. No installed vendor file, saved preference, source mesh, source material or keeper tolerance was changed. New exports were written into `candidate_v001/exports_r002`; the initial exports and failure receipt remain preserved.

## Files and portability

- The original exporter, r002 wrapper, source/GLB keeper, precision helper and diagnostic are at the packet root. `VALIDATED_TOOL_HASHES.json` proves these copies match the tools that produced and checked the saved artifacts.
- `EXPORT_INPUTS.json` retains the exact approved existing source-package/candidate paths and guard hashes. Its sole path relocation moves the retention record from the former scratch location to this packet's approved installed `evidence/INDEPENDENT_SOURCE_RETENTION.json`. The copied retention-record bytes and hash remain identical. `evidence/EXPORT_INPUTS.original.json` preserves the exact earlier input record.
- `NORMAL_PRECISION_FIX_INPUTS.json` pins the exact installed exporter implementation. Unrecognized source roots, changed sources, changed immutable inputs or a different exporter implementation fail closed.
- `evidence/` includes exact original source input pins, retention evidence, preparation hashes and diagnostic results. `receipts/` contains exact source QA, first/r002 export results, first failure and successful r002 equivalence/runtime fragment. `logs/` contains the corresponding execution logs.
- The authoritative source geometry contract, editable source files, archived reference audit and actual GLBs remain in the existing approved parent source package. They are referenced and hash-checked, not duplicated or silently rebound to another working copy.

The validated tools' absolute source guards are intentional. This packet is portable into the approved new tooling folder without relying on the old scratch retention file; it is not permission to target an arbitrary source tree or overwrite a different revision.

## Safe verification

From this packet, run:

```
python run_pure_tests.py
python verify_snapshot.py
```

The first command runs 17 pure tests: five geometry/contact predicates, six triangle/corner matcher tests, and six packet/precision restoration guards. It uses a mocked exporter module for the precision restoration tests and never launches Blender. The second verifies packet hashes and exact existing source/export/retention inputs read-only. While the packet is still in scratch, it remaps only its own approved final evidence path to this local packet for verification. It cannot remap unrelated source paths or escape the packet.

`SNAPSHOT_MANIFEST.json` lists every payload file's exact bytes/hash. The external copy allowlist lists the exact new destination files, including that manifest. Do not merge this packet into an existing tooling folder or overwrite surviving files; the parent should recheck every destination is absent before its guarded installation.

## Reproduction safeguards

The original/r002 export scripts are preserved for reproducibility, but their output paths now exist. Their guards intentionally refuse to overwrite those artifacts or QA receipts. Do not remove that protection, delete first exports, or widen tolerances to repeat a run. A future authorized rerun needs a separately reviewed fresh revision/output namespace and the same source/input guards.

The diagnostic can reopen checked source read-only and write a fresh named diagnostic within its installed tooling directory when the parent coordinates a Blender slot. The preserved `check_contract.py` and `check_planned_contacts.py` are dependencies of the original pure predicate tests; their full generation/preflight entrypoints belong to the parent source package, not a request to rebuild source from this tooling snapshot.

`GREENERY_RUNTIME_FRAGMENT_r002_all.json` is preserved as the successful export-time additive fragment. The parent owns current Game records, commits and future integration decisions; re-copying a historical fragment is not automatically authorized by this packet.
