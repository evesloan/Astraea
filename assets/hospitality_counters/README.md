# Hospitality pantry counter and curved return

Two original editable Blender designs, authored specifically for the independent Astraea catalogue. The dining reference's continuous rounded timber joinery and vertical rhythm inform a shaped guest-facing fascia; its warm lighting is not baked into the materials. The public amenities image supplies hospitality/service purpose only. Historical image labels/counts do not change current canon.

- **AST-HSP-001**: fitted pantry counter, nominal 2.400 m pitch × 0.780 m body depth × 0.900 m worktop height. The staff-side drawer grip projects to Y+0.419 m, so the full evaluated overall depth is 0.809 m. Three accessible service bays, separate removable metal shelves and a shallow open-pan linen drawer support service from the rear.
- **AST-HSP-002**: matching curved return, 90° turn with 0.620 m centreline radius; closed end bulkheads and accessible inner curved shelves. It is a new authored compatible design, not a rotated straight copy. Actual extents are approximately 1.009 × 1.009 × 0.900 m, with a 0.780 m local radial body depth.

The walnut shell has a deliberate bowed/raked section. Broad vertical ribs follow that section; ivory upper and lower rails continue through the return. A single champagne reveal marks the upper seam below the substantial eased stone slab. The service side uses frozen staff-zinc material only on washable shelf/pan/runner surfaces. No luminous strips or amber scene tint are present in either asset.

## Files and reproduction

Editable sources are in `source/AST-HSP-001.blend` and `source/AST-HSP-002.blend`. Static evaluated exports are `exports/AST-HSP-001.glb` and `exports/AST-HSP-002.glb`. The original generator is `source/build_hospitality_counters.py`. Run from any working directory with Blender 4.3.2:

```text
blender --background --threads 2 --python-exit-code 1 --python source/build_hospitality_counters.py
```

The generator intentionally uses the unchanged catalogue `standards/materials.py`, `standards/staff_materials.py` and their original 256px texture files. Source files pack the textures; GLBs embed the actual texture pixels. Keep the family with those relative catalogue paths to reproduce it. No paid/external model, missing-game reconstruction or imported source mesh is used. Script-assisted design is disclosed, not described as manual GUI modelling.

Each source contains named semantic objects and editable edge modifiers. Export consolidation is by functional group and material role, with UV layer names normalized first. Shelves remain separate; the proposed linen drawer has three material groups carrying the same explicit translation metadata. Source drawer meshes are named and share `functional_group=proposed_linen_drawer`; no animation is implemented.

## Placement, contacts and closures

All units are metres. Source +Z is up, +X travels along the initial counter, −Y faces guests and +Y faces staff. Pivot is the entry floor-seam datum. Native GLB coordinates are `(x,z,-y)` from source `(x,y,z)`; actual GLB hierarchy remains authoritative.

`counter_interface.json` records every mating profile. Straight entry is (0,0,0), exit is (2.400,0,0). Return entry is (0,0,0), exit is (0.620,0.620,0) with outgoing +Y. Each module's end surface is inset 1 mm from the nominal seam; adjacent modules have a real 2 mm joint. The inspection pair places the return at source (2.400,0,0), yaw 0°.

Both ends have closed shaped ivory terminal bulkheads beneath a capped stone top. A standalone end is complete; no missing closure derivative is needed. Bulkheads remain in the joined arrangement. No unrecorded open end is concealed by the fixture.

The straight usable worktop support rectangle is X0.060…2.340, Y−0.340…+0.340 at Z0.900. Proposed beverage-station origin is (0.700,0,0.900), subject to the station's own support metadata. There is no raised backsplash. Physical floor and host support records appear in both source and GLB frames in each asset manifest, and are measured against native GLB triangles in `qa/interface_checks.json`.

The drawer's proposed motion is source +Y / native GLB −Z for 0.320 m. Each runner has 7 mm pan-edge bearing at source Z0.646, with 3 mm clearance between the drawer front and the upper rear rail. It is a geometric support/slide proposal only. Full depth including the handle and the full proposed sweep are recorded. No slider implementation or load/food safety assertion is supplied.

## Evidence and scope

- `qa/source_reload_checks.json`: reloads both final saved sources; verifies evaluated bounds, identity scale, semantic UV names, packed texture nodes, no export lights/cameras, exact floor/worktop contacts and connected shelf/drawer support paths
- `qa/glb_validation.json`: independently parses actual GLB chunks, node matrices and accessors; verifies finite triangles, winding, unit normals, nonzero UV area, ordinary semantic materials and embedded texture pixels matching unchanged catalogue sources
- `qa/interface_checks.json`: native GLB triangle contacts, wrong-axis negative controls, measured seam and rear/inner open-space rays with blocked shelf controls
- `qa/camera_preflight.json`: frozen `standards/qa_frame.py` preflight before the four imported-GLB captures
- `qa/render_evidence.json`: exact camera, pose, source/export hashes and import placement for actual pixels. Guest three-quarter, rear service with proposed drawer open, standing eye-height at 640×360, and purposeful seam detail at 1280×960

Source and GLB counts: AST-HSP-001 2,404 triangles, 56 editable mesh parts, 12 exported meshes/primitives; AST-HSP-002 5,730 triangles, 32 editable mesh parts, 7 exported meshes/primitives. Broad silhouette shaping owns the curve budget; tiny hardware does not.

`collision_proposals.json` uses revision `hospitality-static-compound-03`: 34 compound pieces for AST-HSP-001 (previously 26) and 121 for AST-HSP-002 (previously 263). The six-design hospitality proposal therefore has 265 pieces rather than 399. This is a source-backed reduction of 134 pieces, not a runtime performance result.

The return groups contiguous actual source profile rows according to a 5 mm radial chord-error limit. The upper ivory rail uses a tighter 2.5 mm limit to retain a measured 4 mm deep-shelf clearance. Its five fascia height bands are chosen using an exact 2D profile-depth infill bound of 5 mm (actual maximum 3.984 mm). The same correction adds four fascia sections to the straight module. This fixes a real inherited flaw: the old full-profile hull blocked 9–23 mm of usable lower-shelf depth. Two safe shelf/lip consolidations offset part of the straight count increase, and three height cuts per terminal add six pieces, yielding 34 rather than 26. Those cuts are at source Z0.124, 0.164 and 0.580 m, following the toe step and guest-profile curvature. The terminal split preserves an actual small end/plinth recess that the old full-height hull filled. The shell, two ivory rails, stone top, floor plinths, base shelf, top support rail, high shelf upstand, radial supports and closed end bulkheads remain distinct, with source-profile cuts at Z0.124, 0.164 and 0.580 m. A low rolled front lip joins its own shelf; this bounded convexification adds at most about 10 mm locally and does not alter the usable vertical intervals. The drawer keeps its own five pan/wall/front hulls and proposed source +Y / GLB −Z motion. Decorative ribs, thin reveal and drawer grip remain omitted as in Batch07. No collider spans the service cavity.

A collision-only regeneration reads the existing source files, writes only the collision JSON, and hash-checks both source and visual exports. It does not save or export Blender scenes:

```text
blender --background --threads 2 --python-exit-code 1 --python source/build_hospitality_counters.py -- --collision-only
```

Use `--collision-chord-limit-m 0.010` to compare a 10 mm arc budget with the current source-fitted fascia and terminals. The earlier archived arc-only comparisons retain their superseded whole-profile shapes. The default final arc bound is 0.005 m. Full visual rebuilds are unnecessary for this revision.

Versioned evidence is in catalogue-relative `qa/batch08/counter_collision_revision/`. It preserves original proposal/generator/metadata inputs, all prior evidence hashes, the 5 mm and 10 mm actual-source comparisons, and the validation script/report. Tests use actual GLB surfaces, all represented source triangles, the original twelve curved access rays, straight/drawer openings, blocked controls, and finite-size service-sphere sweeps. Conservative radius inflation covers angles and heights between the tested paths inside explicitly bounded service regions; it does not prove general actor fit. The drawer's straight 0.320 m path is checked continuously against static convex geometry, with a blocked wrong-axis control.

The two earlier arc-only candidates (60 or 79 return pieces) are preserved as rejected comparisons: their whole-fascia hull still blocked real lower-shelf depth. Revision03 uses five height bands and clears that depth. Do not confuse the 5 mm *radial chord* limit with an overall 5 mm fit guarantee: shelf/lip consolidation adds up to approximately 10 mm locally, and terminal profiles are decomposed at their real curvature changes. The final terminal refinement costs four more pieces per asset than the toe-only candidate and removes its approximately 21.6 mm guest-side overreach. The report separates represented-source coverage, baseline approximation and current approximation. `deep_corridor_report.json` covers the previously lost shelf depth using a 3 mm sphere proxy and an explicit continuum bound; baseline false-positive controls fail those same source-clear paths. Final independent samples measure maximum outward source-solid overreach of 8.37 mm on the straight shelf lip and 9.65 mm on the curved shelf lip. Fascia maxima are 3.77/7.82 mm and terminal maxima are 2.76/3.19 mm respectively. All represented source triangles are covered, including cap triangles spanning multiple hulls. These are sampled outward errors, not global Hausdorff bounds. These shapes remain unassigned offline data; no engine physics or performance is certified.

All images are neutral Blender component QA, not a restaurant, real room fit, game render, target-PC benchmark, species/accessibility guarantee, physics test or structural/food/electrical certification. Original ship integration remains pending.
