# Forward public core: existing-design derivatives

AST-CIR-005_forward_core is a seventeen-level representation of the existing
AST-CIR-005 enclosure. AST-CIR-003_seventeen_stop is the existing fitted cabin
with its eighteen-stop panel grid restricted to destinations 0–16. Neither is a
new unique design. All earlier source/export binaries and original builders are
preserved byte-for-byte.

## Placement and supported openings

- Local floor heights: 0, 6, 12, 16.5, 21, 27, 35.5, 44, 52.5, 61, 69.5, 78,
  84, 88.5, 93, 97.5 and 102 m
- Intended world translation: `(0, 0, -432)` in glTF/Godot XYZ metres
- Nominal floor boundary: X ±7.8, local Z −13 to +20 m
- Actual enclosure envelope: X ±7.88, Y −0.24 to 105.9, local Z −13.04 to +20.04 m
- Opaque cap: Y 105.78–105.9 m, below the existing D18 datum slab and general
  106.5 m roof datum. Receiving hull/floor contact remains a runtime check
- Front and rear returns both use the 8 m spine; wing guards are present at both
  ends on all seventeen floors
- Only the port side of D01 and D02 has lateral openings. Each opening spans
  local Z −3 to +3 m and has 3.2 m clear height, with a lintel above
- The starboard side remains closed on every floor. Higher port-side walls and
  dados remain continuous until supported lateral branches are built

The lateral opening restriction follows the actual grand-arrivals floor, which
extends from X −8 to 0 at world Z −435 to −429. An opening on the opposite side
would lead off the existing floor. The four lower-level side piers remain outside
the portal at local Z ±3.5.

The section contract retains the original builder coordinates centred at
contract Z −100: Blender `(x, -(z+100), y)`, exported glTF `(x, y, z+100)`.
Receiving code must apply the intended world translation once.

## Editable source and economical exchange

The enclosure `.blend` contains 845 separate named closed meshes and packed
textures. Its GLB contains 10,140 triangles in four semantic-material batches,
with 17 landing and 34 light markers retained. Batching joins meshes only;
there is no remeshing, vertex welding or convexification. Every oriented source
triangle, including its material, is retained in the export.

Use concave triangle collision for these batches. A convex shape around a whole
batch would close the shaft, stair voids and circulation openings. Runtime guard
infill, host floors, stairs, lift cabin placement, gates, collision and lights are
separate integrations; a mesh rail alone does not prove safe collision coverage.

The cabin has 24 editable pieces, seven runtime material batches, 312 triangles,
17 floor-button markers and two light markers. Its physical geometry, material
surfaces and UVs match the original eighteen-stop cabin. Only the panel name and
destination-marker count change; the unused eighteenth destination is absent.

## Reproduction and fresh evidence

Regenerate only in a disposable copy when preserving delivered Blender container
hashes. Dedicated derivative builders cannot overwrite the older masters:

```sh
blender --background --threads 4 --python-exit-code 1 --python assets/primary_atrium_core/source/build_forward_atrium_core.py
blender --background --threads 4 --python-exit-code 1 --python assets/commons_lift_cabin/source/build_seventeen_stop_cabin.py
blender --background --threads 4 --python-exit-code 1 --python assets/primary_atrium_core/qa/verify_forward_source_export.py
python3 assets/primary_atrium_core/qa/verify_forward_glb_bytes.py
python3 assets/primary_atrium_core/qa/reproduce_forward_derivatives.py
```

Fresh saved-source and actual-GLB receipts:

- `qa/forward_core_validation.json`
- `../commons_lift_cabin/qa/seventeen_stop_validation.json`
- `qa/forward_core_glb_bytes.json`
- `../commons_lift_cabin/qa/seventeen_stop_glb_bytes.json`
- `qa/forward_derivatives_reproducibility.json`

Checks cover finite and nondegenerate geometry/UVs, outward source faces, closed
positive-volume source pieces, per-material oriented triangle multiplicity,
source/export vertex and UV correspondence, exact marker sets, cap planes,
portals and continuous wall segments, all end openings and wing guards. An
independent raw-byte reader resolves actual GLB node transforms and probes the
exported triangles. This is independent code, not independent human art approval.

The source-only staging rebuild reproduces both GLBs byte-for-byte without
using any delivered source or export binary as a generation input. Saved Blender
container hashes can vary by staging path; fresh geometry/UV/marker validation
establishes their equivalence. The protection inventory binds all 834 existing
tracked Blender/GLB files and both original builders to the prior commit.

Runtime traversal, actor/cart fit, moving lift behavior, controller interactions,
collision contacts, hull fit, visual review and target-machine performance remain
separate receiving-game checks. This checkpoint does not claim final art or a
complete traversable ship.
