# Optional body-collision selection

This addendum is an optional selection of unchanged convex shapes from the accepted r07 detailed collision proposals. It changes no art, source, export, manifest, marker, detailed collider or image. It is not installed in an engine and does not replace precise interaction or mechanism geometry.

| Asset | Exact detailed profiles | Optional body profiles | Omitted profiles |
| --- | ---: | ---: | ---: |
| AST-CUL-003 audience seat | 43 | 13 | 30 |
| AST-CUL-004 backstage stand | 56 | 30 | 26 |

The seat selection keeps both floor runners, shaped ends, arm caps, navy returns, rear tie, back shell/pad and the complete moving pan/pad. Only its 24 bearing sectors and six pin/retainer/stub pieces are omitted. The stand selection keeps all soles/base, column walls, complete moving cover and pull, tray/gussets/lip, notes face/backer, yoke, housing/shields, diffuser and control. It omits 22 fine aiming-joint pieces plus the internal cable and three clips. Explicit retained/omitted IDs, original owners and omission reasons are in `body_collision_subset.json`; material roles and measurements are in `body_subset_checks.json`.

All 16 primary physical floor/rest/work/grip/control/notes/emitter surface markers remain represented by their unchanged profiles and movement parents. Six fine mechanism contact markers remain available through the unchanged detailed marker API, but are intentionally not body contacts in this optional selection. Every declared use/approach void is copied unchanged. The separate occupied cover-handling reservation still includes the entire cover and pull assembly. No existing hole is filled: for any identical root pose, the selected union is a subset of the detailed union.

## Omission distances, not material thickness

The greatest sampled distance from omitted visual geometry to the retained body union is **56.520 mm for the seat** and **35.000 mm for the stand**. These are distances to remaining collision, not shell thickness, radial clearance or an actor-size tolerance.

The finite tests use every omitted authored vertex and every triangulated convex facet centroid, at 13 seat poses including both endpoints, and at 15 stand combinations of five aiming poses and three cover positions. These samples do not establish a global maximum distance to the union.

Separately, conservative bounds cover every point of each omitted convex solid through every declared rigid motion: **72.002 mm for the seat** and **48.002 mm for the stand**, including a 0.002 mm numerical allowance. Each bound uses one retained convex profile with the same owner. Distance to that convex profile is a convex function, so the maximum vertex distance bounds every point in the omitted convex hull. Identical rigid ownership preserves the bound across all owner poses; other retained profiles can only reduce the distance to their union. This is deliberately a conservative proof, not a measured global Hausdorff distance. Per-shape witnesses, reference shapes, finite worst poses and source/native records are supplied.

The omitted cable/clips are protected inside the closed column/cover. They remain visibly present when the cover is removed, but have no body contact in this optional selection. The omission does not assume that any species is too large to reach them. Service/tool contact, fine picking, radial/axial mechanism work and precise interaction targeting must use the unchanged detailed set and markers. Body proxies do not provide constraints or load-bearing mechanics.

## Two-stage reproduction

1. Rebuild the original family from its accepted original source-only inputs. This produces the detailed `collision_proposals.json`. The previously completed independent r07 rebuild is the Stage 1 dependency; this addendum does not rerun or rewrite that evidence.
2. Run `python actor_proxies/build_body_subset.py` against that generated JSON. The selector rejects a different base hash. `reproduce_two_stage.py` copies the new selector and the independently regenerated Stage 1 JSON into a fresh addendum-only stage, then reproduces `body_collision_subset.json` byte-for-byte without reading a prior body subset as input.

The generated detailed JSON is explicitly a Stage 2 input, not misrepresented as an original clean source input. `two_stage_reproduction.json` binds the original source/exports’ manifests, source files, detailed JSON and independent receipt. `base_byte_lock.json` and `body_subset_checks.json` verify all 305 pre-existing family files stayed byte-identical. The new addendum’s own hashes are listed separately; the original checksum file is untouched.

No Blender or heavy render was run for this addendum. Counts are source-level handoff facts only. Original host geometry, actor sizes, species fit, physics/contact behaviour, engine adoption and runtime performance remain unverified. The detailed profiles remain available whenever these omissions are unsuitable.
