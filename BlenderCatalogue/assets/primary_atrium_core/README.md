# Primary atrium core and upper-link derivative

The existing AST-CIR-005 eighteen-level master is preserved. AST-CIR-005_upper_link
is a reconstructed two-level representation of that design, not a new catalogue
asset ID. No old build or runtime receipt certifies this reconstruction.

## Upper-link placement contract

- Local floor datums: 0 and 4.5 m; opaque cover: 7.73–7.85 m
- Nominal floor boundary: 15.6 × 33 m, identical to the base plan
- Contract plan coordinates retain the base convention centred at z = −100
- Blender coordinates: `(x, -(z+100), y)`; exported GLB: `(x, y, z+100)`
- Intended Godot/world translation, applied by the receiving project: `(0, 102, 119)`
- Actual export envelope including wall thickness, rail ends and pit: 15.76 × 33.08 × 8.09 m in Blender XYZ
- At the intended translation the envelope is world X ±7.88, Y 101.76–109.85, Z 105.96–139.04 m

Both ends return to an 8 m spine. The derivative includes fore and rear wing
rails/posts at both local floor heights. It retains the upper stair-opening
rails and terminal guard. The source has 89 separate editable closed meshes,
six placement/light markers and packed material textures. The GLB has 1,068
triangles. Source and export hashes are in the derivative manifest.

This family supplies enclosure, framing, guards and markers. Floors with actual
openings, stairs, lift cabin, landing gates, collision and working lights are
separate integrations. Rail bars do not establish continuous infill or collision
safety. The isolated cutaway pictures deliberately omit the cover and near wall;
floors, stairs and cabin are absent because they are not part of this export.
They are diagnostic geometry evidence, not a finished room or visual approval.

## Reproduction and focused checks

Use a disposable source copy when regenerating containers. The default builder
variant is `base`; explicitly select `upper_link` to avoid regenerating the
preserved master.

```sh
blender --background --threads 4 --python assets/primary_atrium_core/source/build_primary_atrium_core.py -- --variant upper_link
blender --background --threads 4 --python tools/measure_star_atlas.py -- --asset AST-CIR-005_upper_link
blender --background --threads 4 --python assets/primary_atrium_core/qa/verify_upper_link.py -- --render
python3 assets/primary_atrium_core/qa/reproduce_upper_link.py
```

The reproduction script stages only the builder, derivative contract, catalogue
index and four material PNG dependencies before generation. Neither an existing
derivative binary nor a base binary is present during generation. Only after the
build are unchanged base binaries added for the validator's preservation checks.
The fresh GLB reproduces byte-for-byte. Fresh staged source/export validation
checks the same meshes, markers, materials, UVs and geometry; Blender container
hashes may vary across staging paths.

## Fresh verification boundary, 5 October 2026

`AST-CIR-005_upper_link_geometry_checks.json` records the focused catalogue
measurement. `qa/upper_link_validation.json` binds fresh per-mesh source/export
checks to the current source, export, builder, contract and verifier hashes:

- Zero bidirectional vertex roundtrip deviation
- Position/UV corner roundtrip deviation below 0.000001
- 89 closed, positive-volume editable meshes; outward faces and non-degenerate triangles
- Finite, non-collapsed, metre-scaled UVs on every source and imported triangle
- All six source and imported markers match their declared positions
- All eight end/side/level wing-guard assemblies are measured from imported vertices
- Four end-plane openings are clear in this export over the tested 7.998 × 2.799 m section
- Original base source and export SHA256 hashes remain unchanged

`qa/upper_link_glb_bytes.json` is a fresh raw-byte inspection using the catalogue's
existing separate GLB parser; it reports zero issues. This is independent code,
not a claim of independent human review. `qa/upper_link_reproducibility.json`
records the new isolated rebuild. The two diagnostic captures were inspected for
component placement; independent visual review and in-engine integration remain
pending in this asset checkpoint. No continuous route, fitted-body, loaded-cart,
lift/stair, collision, hull, final-art or performance acceptance is implied.
