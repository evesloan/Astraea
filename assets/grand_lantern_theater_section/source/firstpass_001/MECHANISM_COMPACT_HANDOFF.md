# Final compact mechanism input

Use **`mechanism_package_compact.json`** for the new theater assembly. The full `mechanism_package.json` remains retained unchanged as earlier evidence. Both have the same JSON schema, material-reference contract and append-adapter API described in `MECHANISM_PACKAGE_INTERFACE.md`.

## Reduction and preservation

- Before:1,912 parts,76,524 triangles.
- Compact:880 parts,34,316 triangles. **42,208 fewer triangles,55.16% reduction.**
- All39 motion-group records and all markers are exactly unchanged.
- All478 objects outside the explicitly optimized cap/track/fastener/trolley categories are byte-for-byte equal as parsed JSON objects. This includes the complete retained visible doors/cabin, frames, controls, guide support geometry and secondary mounting brackets.
- All3,312 cap/track bore world-vertex coordinates are exactly identical at1e-9m comparison precision. Channels, outer cap sections, bearing areas and body silhouettes are unchanged.

Compact cost breakdown:

| Category | Parts | Triangles |
|---|---:|---:|
| Visible retained leaves/glazing |111|3,132|
| Retained cabin shell/furniture |7|312|
| Visible frames/controls/brackets |164|2,064|
| Lift guides/posts/head frame |36|432|
| Main caps/heads, exact bores |33|5,364|
| Main tracks, exact bores |21|5,220|
| Main hidden fasteners |120|4,320|
| Main hidden trolleys |36|1,824|
| Gate hidden tracks |160|1,920|
| Gate hidden trolleys |192|9,728|
| Total |880|34,316|

Savings come from three bounded changes:

1. Perforated roof/track plates are closed unified meshes with the exact same hole boundaries. Their previously invisible internal subdivision faces are removed. Every outer/hole boundary and net plate area is checked after triangulation.
2. Hidden integral roller/axle profiles use octagonal six-section geometry. Their complete coordinate bounds and running-track clearances remain within the approved envelopes. Hanger holes use low-poly circumscribed bores preserving the required clearance envelope. The larger visible leaf/cabin meshes are not simplified.
3. Five paired roof-fastener stations per main entrance remain at u=-4.95,-2.70,0,+2.70,+4.95. All46 approved cap/track bores per entrance remain unchanged; unpopulated positions are spare mounting holes. The source still has an explicit distributed track-to-roof attachment path, without modelling every possible fastener position.

No structural-load or actual rotating-bearing-phase acceptance is claimed. As in the full package, phase/contact verification and Blender/export/import checks remain the coordinated source-slot work; compact geometry does not turn prior unperformed tests into passes.

## Explicit generator and adapter

The compact generator is separate: **`build_mechanism_package_compact.py`**.

- `build_mechanism_package_compact.build_package(include_guides=True)` returns compact JSON primitives.
- `build_mechanism_package_compact.write_package()` writes `mechanism_package_compact.json` only.
- The original `build_mechanism_package.py` still regenerates the original full package; it was not silently redirected.
- The compact generator uses existing SciPy/NumPy for checked planar triangulation during pure-data generation. The generated JSON and either module's `append_to_blender(...)` adapter require neither library in Blender.
- Append/material API is unchanged. No bpy import executes until the parent explicitly calls its Blender adapter. Reports contain strings/counts/primitive data, never live material objects.

An independent second generation matches the compact JSON byte for byte, with `allow_nan=False` serialization. Compact SHA256:

`e50fbd0c4018d1ca70af5d863867bf8abb15387e031c99d00e912340682b57df`

## Completed pure checks

- `mechanism_package_compact.checks.json`: finite vertices/UVs, indices, all39 motion groups, and all106 moving lift parts inside the5.34m envelope at closed/open endpoints.
- `mechanism_compact_mesh_checks.json`: unchanged visible geometry/motions/markers; exact cap-bore equality; no negative or zero volumes, no degenerate triangles and no open odd-boundary edges.
- `mechanism_compact_source_contact_checks.json`: zero unapproved contacts during continuous swept-AABB checks against unaffected source parts; exactly24 approved secondary fixed-wall engagements; verified actual foundation-edge and1.5m² solid-head bearing witnesses; all four secondary assemblies remain inside their approved bounds.

Source hash c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5 remains unchanged. No Blender, Godot, runtime or live project writes occurred.

## Cabin practical-light attachment check

`mechanism_compact_cabin_light_ray_checks.json` checks2,728 actual compact moving-cabin/gate/shoe triangles. Both marker projections hit the true underside of `THEATER_CABIN_CAB_lens_0`30mm above the marker, with downward-facing lens normals. Straight downward rays reach the warm-stone platform2.97m below. All66 sampled downward rays have clear50mm exits and actual cabin receivers. Parent may attach its two12W source-preview light trials to `THEATER_LIFT_CABIN` at the unchanged marker positions. This is geometry/attachment evidence, not photometric or image acceptance.
