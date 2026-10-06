# First-pass mechanism source package: stable assembly interface

## Files and entry points

- `mechanism_package.json`: generated pure mesh/spec package; all values are JSON primitives.
- `build_mechanism_package.py`: standard-library-only generator. No Blender/Godot imports execute while building JSON.
- `build_package(include_guides=True)` returns the package dictionary.
- `write_package(output_path=None, include_guides=True)` writes only inside this scratch directory.
- `append_to_blender(package, material_map, parent_root=None, collection=None)` is an optional parent-slot adapter. It imports bpy only when explicitly called, creates editable source objects and real hierarchical motion roots, and does not save/export or run an engine. Its return value contains names/counts only, so it can be serialized.
- `load_retained_materials_for_blender(package)` is an optional parent-slot convenience for loading exact original material datablocks. Its material_map is deliberately transient Blender data; never place it inside a JSON report.

The parent owns loading the original source into the NEW `AST-CUL-005_firstpass_001.blend`, removing the exact six baseline cap parts by their original semantic ranges, and all save/export decisions. This package neither removes baseline meshes nor creates duplicate baseline foundations, gallery floors, chairs, general lighting or ceiling.

## JSON schema

`objects` entries contain:

- `name`: unique semantic source part name
- `vertices_world`: XYZ metres, Y-up, exact closed/rest placement
- `faces`: outward polygon index lists
- `uv_faces`: corresponding per-polygon-corner UV pairs
- `material_ref`: key into `material_refs`
- `material_family`: source role/datablock label
- `role`: `static_mechanism`, `moving_mechanism`, or `approved_cap_derivative`
- `motion_group`: string ID or null
- `catalogue_owner`: existing AST-DOR-002, AST-DOR-003, AST-CIR-003, or AST-CUL-005 identity
- Optional `source_provenance` and `intentional_fixed_bearing`, both primitive dictionaries

`material_refs` maps keys to exact `source_blend` and `datablock_name`. Reuse their original graph and packed textures. Do not collapse merely matching material names across families without checking their signatures. Source datablocks used are ivory_enamel, champagne_metal, warm_walnut, warm_stone, teal_weave, oatmeal_weave, GardenOpalLens, LiftGateTintedGlass, ASTRAEA_champagne_metal and ASTRAEA_staff_bluegrey_paint. The cap parts use the retained original theater ASTRAEA_champagne_metal. Secondary guest infills reuse warm_walnut; the staff derivative uses the retained theater staff-bluegrey material. Lift glazing remains the actual AST-DOR-003 tinted glass.

`motion_groups` entries specify `id`, `parent`, `closed_root_world`, `axis_world`, `travel_m` or `translation_range_m`, and source family. The cabin root is `THEATER_LIFT_CABIN`; its four gate leaves are its children. All other leaves are independent roots. There are39 groups: one cabin root, six main leaves, sixteen lift/cabin gate leaves and sixteen secondary leaves. Scale is always1.

**Do not double-transform world vertices.** If creating real pivot roots at `closed_root_world`, subtract that world root from each moving object's vertices before parenting. A child root's local rest location is its world rest root minus its parent's world rest root. Alternatively keep identity roots and retain the rest-root positions as metadata. The optional adapter handles the real-pivot approach and maps world(x,y,z) to Blender(x,-z,y). Static objects remain in world coordinates beneath an identity-world source root.

`markers` contain world position, kind and motion ownership. They identify source call plates, cabin floor controls, lens attachment points and fixed guide-contact datums. They do not claim active electrical emitters or runtime actions.

## Included geometry

- Three 5.2m main AST-DOR-002 entries: actual retained faceted leaf/inset/seal geometry enlarged by named coordinates, cap derivatives, three new matching heads, true underside track channels, real roof/track bores, supported tracks, low-poly integral twin-roller/axle trolleys, bored hangers, physical call plates and end stops.
- Three landing plus one moving cabin AST-DOR-003 gates: actual retained four-leaf/two-rank framed-glass construction, pockets and separate depth rails; genuinely hollow headers, supported internal guide channels, rollers and hangers. Width3.4m, lift clear height3.0m.
- Four source-approved secondary guest/staff entries: same genuine telescoping family, clear height3.4m, opaque infill, exact200mm assembly depth and24 explicitly tagged approved fixed wall bearings from `SECONDARY_INTERFACE_DOOR_PLAN.json`.
- AST-CIR-003 three-stop cabin enlarged to4.98×4.98m outer bounds, retaining rear chamfers, benches, control panel, inlay and ceiling wells. Roof underside3.17m, lens underside3.00m, roof top3.31m. The4.4m plan turning disk remains clear. Source-derived shape topology and material hierarchy are retained; rigid translated surfaces keep original UVs, dimensionally changed surfaces receive metre-scaled UVs.
- Independent T guides/C shoes entirely within the approved5.34m moving envelope. The guide posts use foundation INNER SIDE brackets atY69.28–69.48,20mm below the pane, and a fixed head frame on solid front jamb/head tops atY87.65. Crossing members start87.70; frame top87.85, below the new91.12 ceiling. No glass support, foundation cut or5.40m expansion.

The source GLBs are decoded directly from their actual BIN vertex/index/UV buffers; their hashes are pinned. Original float32 dimensions are normalized to the nearest micrometre before explicit dimensional extensions. No scene-root/controller scaling is used.

The low-poly trolley simplification uses an integral twin-wheel/axle surface rather than separate manufacturing hubs. It keeps the approved envelope and has a real complementary hanger bore. Actual rotating wheel phases, bearing dynamics and contact tolerances still need source-slot review; no motor/belt/brake or structural-load certification is claimed.

## Pure checks completed

Current package:1,912 semantic mesh parts,76,524 triangles after fan triangulation,39 motion groups and106 moving lift mesh parts. All vertices and UVs are finite; indices match; every source input hash is unchanged.

- `mechanism_package.checks.json`: closed/open whole moving lift envelope passes5.34m bound. Vertical translation is bounded continuously by the existing approved interval.
- `mechanism_mesh_orientation_check.json`: no negative/zero signed volumes and no degenerate triangles. Minimum triangle area about1.82e-8m².
- `mechanism_closed_mesh_checks.json`: no open odd-multiplicity boundaries after position welding at1e-7m. Thirty-three retained closed compound mesh objects have shared even-multiplicity edges; these are not missing boundary faces.
- `mechanism_source_contact_checks.json`: all actual generated vertex AABBs continuously swept against every unaffected retained source part. No unapproved positive-volume contacts. Exactly24 approved secondary fixed-wall engagement contacts. All four secondary door sweeps remain inside their approved clear assembly boxes.
- Guide foundation contacts are witnessed against the actual approved foundation polygon edges at X=-44.25 and-38.75, Y69.28–69.48. The head front beam has1.5m² of exact top bearing across the original solid port jamb/D13 head/starboard jamb atY87.65.
- `mechanism_leaf_endpoint_bounds.json`: complete leaf/hanger/trolley closed/open bounds, including the meeting seals.

These checks do not replace Blender roundtrip, full internal triangle/rotating bearing-phase checks, imported source/collider verification, physical cart/species routes, actual control behavior or runtime tests. The Godot project remained frozen and no engine process was started.
