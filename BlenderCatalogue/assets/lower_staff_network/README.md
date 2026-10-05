# AST-STF-009: screened lower staff network

Editable construction kit for one port-forward D01/D02/D03 staff lift enclosure and its service routes. This is not a completed home, depot, staffing system or final-art acceptance.

## Authoritative component files

- `source/section_contract.json`: exact world-space floor union polygons, supported interface apertures, shaft exclusion, dynamic lift transform, clearances and all 99 task-light markers
- `source/AST-STF-009.blend`: 1,605 separately editable closed outward source pieces; packed staff material textures
- `exports/AST-STF-009.glb`: 19,260 triangles in 281 spatially bounded material batches, each at most 20 m in X and Z
- `source/geometry_parts.json`: exact authored cuboid bounds for reproducible interface tests
- `qa/source_export_validation.json`: geometry, UV, equivalence, light-exit, interface, hull and protected-file evidence

World placement is identity at Godot origin. Blender coordinates are (Godot X, −Godot Z, Godot Y); ordinary Y-up GLB conversion restores Godot XYZ.

## Integration and ownership

No general floor slabs are included. The integration task owns the disjoint union, subtraction of existing floor allocations and 24 cm structural slab generation. The only horizontal floor component here is the shaft pit pan, Y−0.24..−0.20. The shaft cap is Y 15.10..15.24, safely below the D04 slab underside 16.26.

Reuse the existing `commons_lift.gd`, `AST-CIR-003_three_stop.glb` and `AST-DOR-003.glb`. Place the lift under a parent at (−25,0,−490), rotated PI around Y, with local gate origin (−1.8,0); stop elevations are 0, 6, 12. Do not duplicate, rewrite or bake dynamic parts into this static export. Keep collision concave per actual static batch; a convex hull across the corridor or shaft would block circulation.

The dynamic gate retains its actual 2.4 m clear width and 2.65 m clear height. All leaf depth channels remain clear. The cabin has 40 mm side clearance, 160 mm rear clearance, 160 mm top clearance and 20 mm clearance above the pit pan. The floor shaft exclusion extends east to X−23.18, 20 mm beyond the cabin front. The existing fixed sill bridges that contact tolerance; it is not an enlarged gate. All three corridor ceilings subtract the same shaft-clearance rectangle. The complete moving cabin swept AABB, inflated by 5 mm on every face, clears every authored piece.

Corridors are 3.6 m gross width, with 120 mm walls and 25 mm projecting cart bumpers: minimum straight/cart-corner clear width 3.31 m. Ceiling underside is 3.20 m; lowest task-lens underside is 3.015 m. D01/D02 destination apertures remain 3.20 m high. Real loaded-cart turning is an integration test, not proved by these planar dimensions.

The D01 connection remains open to the port service spine. Both wall/bumper returns end at X−48; no 2 m nib protrudes into the existing longitudinal street. The D02 opening fits its existing fusion-service opening and screened approach. D03 home and depot are closed, bounded thresholds, each 6×6 m gross, with no onward entrance into unsupported space. No Arrivals spur, crew bed, job or species assignment was added.

## Fixtures and batching

Exactly 99 `DATUM_light_Dxx_yyy` markers match physical source lenses. Each lies 10 mm below the lens underside and has a verified clear downward exit to its deck. Use the existing staff lighting profile and runtime lighting budget. Source preview area lights are diagnostic only and are not exported.

Mesh batches are keyed by deck, 20 m X/Z cell and material. Keep the bounded cells for Compatibility per-object lighting. The source remains fully unbatched/editable. Metric UVs use existing staff-material tile sizes; source/export triangles, materials and UVs are equivalent at 1 mm signature precision, with zero vertex-position error in both directions.

## Rebuild and verify

Run Blender 4.3.2 or the established compatible Blender version:

    blender -b --python assets/lower_staff_network/source/build_lower_staff_network.py
    blender -b --python assets/lower_staff_network/qa/verify_lower_staff_network.py
    blender -b --python assets/lower_staff_network/qa/render_source_preview.py

The builder asserts that AST-STF-009 is unused or already belongs to this family. `make_section_contract.py` reproduces the unlit coordinate contract; the builder appends the exact marker list.

`source_landing_preview.png` and `source_corridor_preview.png` are inspected Blender-only diagnostic renders with temporary union floors and imported existing lift components. They are not in-engine evidence. Godot motion/boarding, complete player routes, loaded-cart physical turns, fixture lighting/occlusion and final visual acceptance are owned by the parent integration task. No Godot production files or prior catalogue assets were modified by this authoring task.

## D02 fusion interface closure revision

Five fitted jamb/header pieces close the measured 200 mm side slots and 50 mm axial gap at the existing fusion opening. The existing AST-ARR-002 GLB was measured directly: wall X−53.9500008..−53.75, opening Z−434..−430, header underside Y9.1999998. The new collar occupies X−54.12..−53.77, with side strips outside the full 3.6 m transition aperture. Its header underside is Y9.205, preserving at least 3.2 m headroom and avoiding coplanar flicker.

The five exact permitted names and supported footprint are in D02's interface_extensions. All 45 sampled support points lie on the retained D02_fusion_screened_service floor. No floor slab or general union polygon changed; ordinary containment remains strict. The 1,600 pre-collar pieces, all materials and fixtures are unchanged.

qa/fusion_collar_validation.json records 2,356 closed side-seam rays, 273 closed header-seam rays and 1,085 unobstructed aperture rays against the actual combined GLBs. Run qa/verify_fusion_collar.py with Blender to repeat. The diagnostic source preview is separate from the parent's in-engine visual acceptance.
