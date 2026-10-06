# Inward stair channels 021: completed source-only export

The frozen two-thread export job completed successfully on 2026-10-06 at 20:29:00 UTC. The source snapshot, new GLB and independent binary QA are in `run001/`. `README.md`, `EXPORT_PLAN.json` and `PREPARATION_REPORT.json` are preserved historical preparation evidence; this file records the completed outcome.

## Actual outcome

- Source: already-retained `assets/grand_lantern_theater_section/source/stair_inward_channels_020/AST-CUL-005_inward_stair_channels_020.blend`
- Source SHA-256: `fd454d55af4718f8cd3458223c87f0c8fa83f9fe3ad514c94486d7ce87885ef8`
- GLB SHA-256: `845d1ebf550de3690abbf5bab5a10e14d2b8273e8227531e05e99cf10acfc2e3`
- Independent binary QA SHA-256: `556d512f2d6b99b8756ccf9358cf9cb2863508f1dcce099cb6f82f70850563aa`
- Exactly 24 meshes / 416 triangles, eight lens-parented non-light attachment empties and eight local grouping roots; 40 nodes total
- Zero source-to-binary position error, exact local position/float32 UV storage, maximum normal error 5.301152304656712e-8
- Both retained material graphs, packed PNGs, shader values, sampling and per-face metric UVs preserved
- Eight verified optical exits, approximately 4.000457 mm from the physical lens to its attachment point
- All 90 tread-center rays clear; no new fixture blocks any of the 450 center/corner diagnostic rays

## Important lighting limit

The 450 diagnostic samples preserve 62 retained-geometry occlusions before the corner receiver and 118 exact shared-boundary endpoint contacts. The remaining 270 samples, including every tread center, are clear. This does not establish uniform or complete tread-surface lighting, native visibility, shadows, fixture selection, engine budgets or final visual acceptance. Source energy remains unset and no runtime light was created.

`NATIVE_RECEIVER_PLAN.json` is explicitly a future, unsaved native-trial plan. It records geometric cone/range requirements only, retains the 4.8–5.7 m ranges, and does not set energy or imply native acceptance.

## Retention and boundaries

The package preserves exact executed scripts, pinned helper dependencies, reports, logs, GLB and actual-source array snapshot. It excludes caches and does not duplicate the full editable source. `INPUT_REFERENCES.json` maps the already-retained source and retained original context by path/hash.

The scripts retain their original execution paths as provenance. They are not a runtime installer. The source job refuses an existing `run001`, preventing an accidental overwrite of this evidence. No source save, render, Game change, runtime installation, registry change or native engine trial occurred in this export job. Copying this new-only package is not itself independent remote retention; that remains a separate verified publisher result.
