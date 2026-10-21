# Night Garden D15 partition successor — 21 October 2026

The retained 30-room r002/r003 district now has 60 independently loadable saved scenes: one always-resident architectural shell and one private-detail scene per room. This completes the missing source-preserving partition preparation. It does not install the district, add rooms/capacity, remodel its native sources, or certify private-residency behavior.

## Provenance and preservation

Base: private evesloan/Astraea construction head e6274e7700840d811710d34acc8cb6ce535f68c7, rechecked through existing Git transport before work. Recovery independently verified every tracked source blob. PREIMAGE.json records 104 checked source/native/helper pins, all unchanged after this step. Existing r002 rooms, r003 receiving, original commons, 80 adopted homes, ship, Central Homes, source archives and original checkout are preserved. No existing tracked file was edited.

The new baker derives from the retained bake_private_shells.gd, uses the exact R003_PRIVATE_PARTITION_PROPOSAL names, and refuses existing output paths. It reads raw GLBs through Godot 4.6.3 GLTFDocument, so it requires no full-project import. It detaches owned resources and writes separate shell/detail scenes under assets/runtime/night_garden_partition_20261021. Original materials and source pixels are preserved; no flattening, simplification or new geometry was introduced. Source-native authorship remains in the retained Blender catalogue.

## Focused evidence

BAKE.log: one completed sequential bake, exit 0, no engine/script errors.
VALIDATE.log and EXACT_PARTITION.json: separate process reopened all saved scenes against freshly read source GLBs; exit 0, no engine/script errors.

- 30 exact source allocations; 210 always-resident architecture/mixed meshes; 1,909 deferred detail meshes.
- All 2,239 surfaces preserve arrays (vertices, indices, normals and UVs), primitive type, exact transforms, material storage properties, texture image dimensions/format/mipmaps/pixels, visibility/layers/shadows and collision/material-role metadata.
- Every source mesh belongs to exactly one partition. Shells omit all private detail; detail scenes contain no architectural mesh resources.
- Saved scenes have no dependency on full original GLB scenes.
- 90 detail instantiate/free cycles (three per room) pass; no saved detail PackedScene remains strongly cached after each cycle.
- 104 preimage pins pass again. This is resource identity/release evidence, not player/cart contact-transition or measured shipwide memory acceptance.

## Integration remains held for specific reasons

The retained r003 district builder still calls its eager contact_visual helper. It does not consume this new partition index. Applying its proposed two-line main hook now would bypass the mandatory private-residency guard and eagerly instantiate the 30 detailed interiors.

The proposal's startup ship snapshot hash also differs from the independently retained current ship; the six other hook pins match. The current ship is preserved, not reset to that snapshot. Its actual vertical_commons-before-Central-Homes ordering was inspected, but this alone is not sufficient adoption evidence.

Next coherent step: a named district/residency adapter successor consuming this exact index and detached detail scenes, retaining all architectural shells, doors, lights and identities; focused near/far and visibility/physics transitions with the actual controllers and exact commons wall-contact ownership; then the single coordinated current-owner hook. Reconcile current startup ownership and normal import equivalence without making exhaustive whole-ship startup/gameplay a substitute for this work. Do not regenerate these 30 source rooms or bake these outputs again.

The r003 receiving and its bounded portal seam repair remain unchanged. Connected actual-player routes, entry-door/private admission, cart/species/engineering, contextual materials/lighting/CRT visual review and final ship acceptance remain open. No new screenshot, full startup run, global material pass, publication retry or backup process was performed. Missing later tram-intro and R00358 source are not part of this package.

## Outputs and retention

Index: data/architecture/night_garden_partition_20261021/index.json.
Recipes: tools/night_garden_partition_20261021/bake.gd and validate.gd, with exact input.json.
CHANGED_FILES.json records SHA-256 and sizes for this successor's files, excluding itself. A local commit is a local checkpoint only; independent remote retention of this new work is not claimed. Publication is left untouched because the earlier approval/publication outcome remains unresolved.
