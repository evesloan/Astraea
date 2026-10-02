# Staff cabinet hinge coordinate metadata revision 02

This folder preserves the exact eight original top-level inputs and the evidence for a metadata-only asset-content correction. The GLB edit changes hinge extras only, with its complete BIN payload and every JSON value outside those extras unchanged. The editable source is reserialized after changing only hinge properties; all recorded asset geometry/material/hierarchy/transform/texture invariants pass after reload. Blender window/layout state is outside this preservation claim.

- `verification_report.json`: current hashes, changed file list and evidence index
- `original_inputs_manifest.json` and `original_inputs/`: exact historical inputs
- `source_preservation_report.json`, `source_before_snapshot.json`, `revise_source_metadata.py`, `source_revision.log`: source comparisons and procedure
- `glb_preservation_report.json`, `revise_glb_metadata.py`: surgical GLB update and byte/JSON checks
- `generator_smoke_report.json`, `generator_smoke.log`, `generator_sandbox/`: isolated reproduction using copied shared dependencies; parsed JSON and BIN exactly match the current GLB

Existing asset and Batch03 render/sweep/validation reports were not rewritten or rerun. Their old hashes refer to the preserved original inputs. No render, engine scene, gameplay or new unique asset was created.
