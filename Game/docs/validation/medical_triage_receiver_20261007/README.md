# Medical triage receiver validation successor — 7 October 2026

The source model represents WALL_DIFFUSER as an authored physical receiver marker, while its visible wall_recessed_diffuser is consolidated into AST-GST-002__oatmeal_weave. The old validator incorrectly required the marker itself to be a mesh. This three-file successor keeps the runtime source marker identity, resolves exactly one same-owner semantic diffuser mesh, and checks its actual visibility, physical marker coincidence and existing light-housing tolerance. All source assets, fixture positions/aims, optics, room geometry, controllers and physics remain unchanged.

## Actual results

- Registered medical_structure: PASS after its import barrier. 34 housed lights, 23 new fixtures (8 marker-backed and 15 direct meshes), 448 room mesh bounds, 16 static privacy leaves, 81 triage aperture rays, and 852 unchanged imported core meshes.
- Registered medical_access: PASS. The same player walked all eight rooms and returned to the core over 371.755m with no later teleport.
- Registered medical_cart: FAIL at the post-quarter-turn actual yaw check. The preceding room-center-distance check passed; the original receipt did not record which pod or the actual pose. Do not call this complete loaded-cart room acceptance.
- Registered lighting_budget: PASS in a separate serialized run after the cart chain stopped. The eight-source cap and existing selection checks remain intact.
- Read-only source correspondence: all 23 mappings and source-predicted bounds pass; seven invalid mapping mutations are rejected. This alone is not runtime proof.

See SUMMARY.json, the unmodified runner logs/receipts in runs/, and detailed attempt receipts in attempts/. Source-preservation attestation covers all 5,163 recovered Game inputs: only the three exact successor postimages changed, with 5,160 files unchanged and no missing/unexpected source paths.

## Scope and retained history

The source history is based on 72278108ec13262420f9397d7e861436e95dbe9f with recovered WIP from independently retained main 7e220d0ef7e03acafabecfbe34b0c277e94619c3. All three edited paths already included an earlier static-leaf metadata/scope correction in that recovered WIP. Their exact preimages and EXACT_DIFF.patch distinguish that predecessor from the new receiver fix. A narrow source commit does not by itself contain the whole tested WIP; keep its associated complete checkpoint.

MANIFEST.json is the unchanged original preparation record. ROOT_APPLY_RECEIPT.json records later application under verified independent protection; SUMMARY.json records actual subsequent tests. Earlier false/pending fields are historical, not current results. Failed cart evidence is retained as failed. A separate observation-only diagnostic is the next step for the cart and is not included as a claimed repair here.

## Reproduce and reverse

For source-only checks, run Python 3 with NumPy: python reproduce_source_receivers.py --root /path/to/Game --output /path/to/new-output. The source checker does not launch Godot or write the project.

Runtime checks must follow current repository protection/resource rules and the single serialized Game engine slot. Use the registered runner: python tools/validate.py --only medical_structure (and separately medical_access, medical_cart and lighting_budget). Do not alter watchdogs, frame caps, assertions or physics to obtain a pass.

EXACT_DIFF.patch maps the retained recovered preimages to exact postimages. Reversal is authorized only when current file hashes still match the recorded postimages; preserve any later edits instead of applying a blind reset. The preimages retain the earlier recovered WIP, rather than reverting to source HEAD.

These are focused source/physics checks, not final art, medical operation, species capacity, freehand comfort, target-GPU performance, completed-department or full-suite acceptance. Privacy leaves remain static with door operation unaccepted.
