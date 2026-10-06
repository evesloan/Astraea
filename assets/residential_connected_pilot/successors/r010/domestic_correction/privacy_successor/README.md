# Current residential optical-privacy successor

Authority: Eve's 2026-10-06 22:34:48 instruction, Sentinel_1367a9f10c748191835bf2083b1308da. Every residential occupant retains a useful outward view, while public/court and opposite-suite observers must not see any suite interior. This replaces the earlier direct sleeping cross-court allowance. FULL_FAMILY_PRODUCTION_MATRIX_CURRENT.json changes only the privacy clauses and explicit authority metadata; all counts, allocations and tier/species distinctions remain intact.

The 85-file corrected-source snapshot at Catalogue commit 2d5ca4ea971cd9523cae5e619ec57d1b950e5469 is deliberately retained as the pre-privacy candidate. This separate successor does not rewrite it.

## Optical profile

Apply only to the finite residential window mesh. A clear low-opacity interior material and a genuinely opaque polished/tinted exterior material share that exact mesh. The exterior shader never reads or writes ALPHA, so it remains in the opaque pipeline and is not a dark transparent coating. A per-aperture world plane and inward normal select the correct side for each camera. The 15 mm near-plane band fails closed. The profile is explicit fictional/game optical behavior, not a claim that ordinary one-way mirrors guarantee privacy under arbitrary lighting.

Godot's shader reference documents that ALPHA sends a material into the transparent pipeline, where sorting issues can occur. This is why the exterior is a separate opaque pass: https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/spatial_shader.html . CAMERA_POSITION_WORLD permits per-camera side selection in the same renderer.

Call scripts/residential_privacy_glazing.gd::apply_to_pane(pane, plane_origin_world, unit_inside_normal_world, stable_suite_identity). The helper creates one shared-mesh, collider-free exterior child. The original pane's physics stays in its normal owner. Shadow casting is disabled for these optical coatings. Court/rail and shower glass keep their existing materials. The interior shader filename deliberately contains `glass`, preserving the existing LightingBudget transparency-ray convention without changing that global system.

## Reference inspected

Author personally opened /workspace/scratch/375c2e438292/reference-window-privacy-20261006/515c9925-2338-485c-866d-c5378a82acb4(2).png. Its warm local fixture lighting, dense lower planting, hanging gallery layers and bed/social outlook guide native review. Any opposite interiors visible in that image are superseded by the explicit privacy instruction. Existing master chapters 5/6/21/32 and the earlier full reference inspections are retained with the source package.

## Required native proof

No engine validation has yet occurred for this successor. Inspect a clear interior court view before adding planting. Then test room lights on and off, front/near/far public cameras, opposite-room positions and oblique/grazing/edge views. Temporary labelled unshaded magenta/cyan targets may be used to detect interior leakage pixel-by-pixel; remove them before natural captures. Exterior renders must not depend on the hidden target's color, while a court-side target must remain visibly different from an inside camera. Check gaps at pane/frame junctions and the near-plane cutoff. Use the current Compatibility renderer and LightingBudget, and leave all public glass unchanged.
