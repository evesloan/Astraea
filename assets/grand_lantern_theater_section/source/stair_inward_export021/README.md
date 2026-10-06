# Inward stair channel export 021: preparation only

No Blender, Godot, renderer or exporter has been launched. No GLB exists. This folder is a reviewed-job candidate; pool and medical source slots, the full119 Game freeze, Catalogue sources and existing exports have not been touched.

## Exact input and output

Input: retained `assets/grand_lantern_theater_section/source/stair_inward_channels_020/AST-CUL-005_inward_stair_channels_020.blend`.

Source SHA-256: `fd454d55af4718f8cd3458223c87f0c8fa83f9fe3ad514c94486d7ce87885ef8`.

Proposed new scratch output: `run001/AST-CUL-005_inward_stair_channels_021.glb`. The entire `run001` directory must be absent before launch; any failed attempt is preserved and prevents repetition into that directory.

## Bounded job for later source-slot release

1. Read-only Blender snapshot of actual evaluated mesh corner arrays, world/local transforms, material graphs, packed-image metadata and object properties. Two threads, 120-second limit.
2. Read the source again and export one GLB under eight local per-flight roots. Two threads, 120-second limit. No source save or render.
3. Independent pure-Python binary verification. No engine, 90-second limit.

The two Blender processes are strictly sequential. OMP is limited to two threads; numerical-library workers are limited to one. Nothing writes Game or Catalogue. The source and all pinned retained inputs are checked before, between and after phases.

The existing three mesh origins within each flight are identical. The export root takes that exact shared origin; original mesh-child transforms become identity, while their actual local coordinates stay unchanged. Existing attachment empties remain parented to their actual lenses with unchanged local transforms. The eight added roots are only organizational: output inventory is 24 meshes, eight existing source attachments and eight grouping roots, or 40 nodes total. The geometric content remains 416 triangles. No original reference meshes, cameras, lights, skins or animations are exported.

## Binary checks

- Reuse the retained strict GLB decoder, complete cyclic-winding triangle matcher and material/image verifier; copies in `dependencies/` are byte-identical and mapped in `TOOL_PROVENANCE.json`.
- Require an exact multiset of local corner positions and float32-representable UVs, with cyclic winding and per-corner associations preserved. No rounded position hashes or tolerance-based welding.
- Compare actual source-world arrays and transforms independently; retain the established 50-micrometre world-representation ceiling and 2e-6 normal ceiling, while local positions/UV storage must match exactly.
- Preserve source mesh names, source properties, eight lens-parented attachment transforms and their energy-unset semantics.
- Verify all material assignments, actual Principled factors, culling, metadata, packed PNG bytes/resolution, samplers and metric UV channels.
- Check every triangle for degeneracy and normal orientation, and each mesh for positive volume.
- Recheck eight physical lens optical exits and all 90 clear center rays using decoded GLB vertices and attachment coordinates.
- Recheck all 450 center/corner samples. Preserve the known 62 retained-geometry pre-receiver occlusions and 118 shared-boundary endpoint contacts. No new fixture may block a ray. Full-tread/native illumination is not claimed.

`precise_normal_export` is the retained process-local normal precision helper. It temporarily changes the export module's normal rounding from four to eight decimal places, restores the value in `finally`, and does not edit the installed exporter, source or preferences.

## Preparation verification

All Python files pass syntax inspection. Fifteen pure adversarial tests pass, covering cyclic reordering, reversed winding, triangle loss/duplication, one-ULP local-position and UV edits, normal changes, shader-factor/emission edits, texture-byte changes, UV transforms and missing attachment semantics. These tests validate the checker, not an export that has not yet run.

`run_export_job.py` defaults to a read-only preflight. An engine run requires both explicit `--run --source-slot-released` flags and the exact parent-reviewed manifest digest through `--manifest-sha256`.

Review `EXPORT_PLAN.json`, `EXECUTION_MANIFEST.json`, `TOOL_PROVENANCE.json`, `preparation_tests.log` and `PREPARATION_REPORT.json`. This preparation does not authorize a launch, render, engine switch, native import, lighting trial, runtime installation or Catalogue overwrite.
