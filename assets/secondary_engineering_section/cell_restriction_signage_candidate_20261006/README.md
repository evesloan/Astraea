# SunCorp restricted cell signage candidate

This additive source supplies a thin enamel plate on the existing east header and printed letters on the existing sliding glass leaf. The requested phrase reads `SPECIALIZED / SUNCORP / PERSONNEL ONLY`. The fixed header reads `SUNCORP · RESTRICTED ENGINEERING`.

Authoritative editable source: `source/AST-ENG-008_cell_restriction_signage_v2.blend`.
Authoritative export: `exports/AST-ENG-008_cell_restriction_signage_004.glb`.
The source keeps four editable Font objects and their backing authoring object hidden beside the two exact, visible, UV-authored export meshes. This is an additive same-family derivative of AST-ENG-008, not a replacement of the installed section or its glazing.

## What passed

- 119 actual existing-header backing samples and 119 exact sliding-glass samples.
- Ink remains inside the unchanged original leaf envelope throughout 41 sampled poses; no new collision, target, floor or light.
- Reopened canonical source and actual export agree exactly on all 6,672 oriented triangle/material/position/UV records. Normals are finite and unit length; no degenerate geometric or UV triangles remain.
- All original source and installed cell-model hashes remain unchanged.

## Visual limit

The initial composed source views show a real limitation: the outward-facing header and ink receive little direct illumination from the frozen five source fixtures. They appear as dark silhouettes. These source-only images are not normal Godot presentation acceptance. Larger labels alone do not resolve that lighting condition. Matching actual Game views are required before claiming readability; if they fail, review a genuinely supported source-light solution rather than increasing ambient/fill or bypassing source selection.

No source fixture, world strength, exposure, old glass material, shared shader or light profile was changed. Final views use the same framing and fixture state with more samples. The installed Blender build does not support its requested denoiser; that failed attempt is preserved and final images use raw sampling.

## Preserved attempts

The initial Font export included eight exactly zero-area collinear fill triangles. The first cleanup used Blender's single-precision face-area predicate and found only six. The corrected float64 cross-product predicate removed exactly the eight independently identified nondrawable triangles. A separate UV audit found degenerate automatic Font UVs; the final visible source meshes use face-local metre-scaled UVs with the original material graphs. All prior exports/scripts/logs remain preserved; the corrected source and export are explicitly named above.

## Runtime limits

Nothing in this package is installed. Directly instantiate the new PackedScene without blanket trimesh attachment. Keep its fixed header sibling separate; reparent only the printed-ink group to the original leaf while preserving global closed-rest placement. The original 153 source groups, gate mesh/collider,120 actuators and old controller remain authoritative. A test that counts recursive descendants must classify the one exact additive print child rather than dropping the original identity census. Per-asset compression disabling for the new thin-ink GLB requires review. Full department first-pass remains false.

See `source/RUNTIME_SIGNAGE_PROPOSAL.json` and the exact QA receipts. All imagery is source-only, with no hidden walls, extra fill or new light.
