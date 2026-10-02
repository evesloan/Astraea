# Aster dining-service furnishings — Batch07

Two original editable Blender 4.3.2 designs, authored with the local reproducible Python generator. These extend the independent component catalogue while the original game remains unavailable. They are neither recovered game source nor a replacement room/player cart.

- **AST-HSP-005 Aster plate and tray service credenza:** 1.10 × 0.78 × 0.90 m. A rounded stone worktop, raked/bowed walnut guest face with broad timber flutes, shaped ivory end cheeks and four supported leveling feet. Staff access is from +Y. Three left shelves carry contextual trays; two right shelves carry coupe plates. Ten folded cleats visibly connect the shelves to the cheeks/divider. Tray support heights are 0.245, 0.473 and 0.701 m; plate support heights are 0.245 and 0.535 m. The rear remains physically open.
- **AST-HSP-006 Aster two-tier dining service trolley:** 0.68 × 0.644 × 0.944 m including rear push grip. Lower/upper inset contacts are 0.231/0.791 m, with useful clear space between. Rounded ivory tiers, walnut perimeter joinery, three-sided retention rails, swept load supports, a connected rear grip and four separate fork/bearing/axle/wheel assemblies. The axle and swivel hierarchy describes proposed articulation only. No rolling, cargo physics, player controls or game integration exists.

## Use and coordinates

Metres. Floor origin is the XY centre; Blender source is Z-up, guest front −Y and staff rear +Y. Standard native GLB mapping is (x,y,z) → (x,z,−y), so front is GLB +Z and staff approach −Z. Actual exported marker nodes include support contacts, floor contacts and the trolley grip. Wheel centres, fork/swivel pivots and both source/native axes appear in the individual manifests and actual node extras. Any receiving engine must resolve the node hierarchy rather than remap already-exported data.

The common proposed serving tray is 0.45 × 0.32 m. Storage contains six identical tray parts and eight identical plate parts; the trolley includes one lower-tier tray derivative. These are configurable stock groups and are **not additional counted designs**. Every stock group is separate in the exported hierarchy and can be omitted by a future consumer. Actual contact-derived nesting is used: tray pitch 0.021 m; plate pitch 0.0114754098 m, where the upper foot meets the lower coupe's inside surface. Stock does not float.

The storage credenza is a freestanding companion to the 0.90 m-high, 0.78 m-deep pantry family. No structural mating joint or approved room footprint is claimed. Keep the numeric staff approach and rear extraction space in the manifests free. The trolley upper inset has room for the shared tray envelope. Grip and wheel records remain proposals pending an original-engine/actor review.

## Runtime cost and material craft

| Design | Complete triangles | Furnishing/castors | Configurable stock | Meshes / primitives |
|---|---:|---:|---:|---:|
| AST-HSP-005 | 10,468 | 4,748 | 5,720 | 11 / 11 |
| AST-HSP-006 | 5,816 | 5,540 | 276 | 18 / 18 |

The storage's contextual plates/trays account for more than half its displayed triangle total. This is reported explicitly, without arbitrary certification or hidden counts. No new LOD is claimed. Static evaluated export geometry is consolidated by material within each functional group; stock and proposed moving castors stay separate. The editable source keeps semantic meshes and construction edge modifiers.

Frozen guest roles are ivory enamel, warm walnut, champagne metal, dark rubber and, on the credenza, warm stone. Staff zinc is explicitly limited to washable stock/inner surfaces and mechanical castor parts. All texture pixels are the existing original catalogue tiles. Active UVs are normalized to `metric_material_uv`, measured in the material's metres-per-tile scale; the tall walnut face grain runs vertically. No reference-image pixels are reused as textures, and no old assets/material helpers were edited.

## Evidence and limitations

- Actual source reloads check packed referenced images, positive transforms, retained editable parts/modifiers, floor contacts, shelf-to-cleat support and every stock stacking contact.
- A separate binary GLB parser checks triangle counts, hierarchy/world bounds, finite positions/normals/UVs, winding against normals, noncollapsed UV areas and exact embedded texture pixels.
- Native GLB hierarchy checks bind every physical contact marker to an actual surface ray. Castor pivots and transformed axes are checked with sensitive wrong-axis controls. The proposed full swivel radius is bounded against actual geometry, without simulating motion.
- `collision_proposals.json` contains numeric split boxes/cylinders/capsules in both asset-datum source and native GLB frames. These preserve compartments, tier approach and the space below the grip. Five opening volumes are checked against actual fixed-geometry triangles and the proposals; deliberate blocked controls are detected. Stock collisions/dynamics remain excluded proposals.
- Imported-GLB neutral ordinary, staff standing-eye/use and detail views are captured after `qa_frame` preflight. Lights, floor and cameras are QA aids only, with exact file hashes and camera parameters recorded.

The actual public blueprint and dining-edge image were inspected. Their dining-service purpose, continuous rounded joinery, ribbed timber and integrated presentation guided these original forms. Historical image labels/counts do not alter current ship canon. No new capacity, species fit, accessibility, food-service, structural, balance or safety certification is implied. There is no controller, game scene, replacement ship, runtime physics or player-cart claim.

## Reproduce

From the catalogue root:

```sh
blender --background --threads 2 --python-exit-code 1 --python assets/hospitality_serviceware/source/build_serviceware.py
python assets/hospitality_serviceware/qa/validate_glb.py
blender --background --threads 1 --python-exit-code 1 --python assets/hospitality_serviceware/qa/inspect_source.py
python assets/hospitality_serviceware/qa/inspect_exchange.py
blender --background --threads 1 --python-exit-code 1 --python assets/hospitality_serviceware/qa/render_imported.py -- --preflight
# Coordinate the heavy render slot before the next command.
blender --background --threads 4 --python-exit-code 1 --python assets/hospitality_serviceware/qa/render_imported.py
python assets/hospitality_serviceware/qa/label_views.py
python assets/hospitality_serviceware/qa/finalize_records.py
```

`dependency_manifest.json` lists the immutable shared generator/material/reference dependencies. Both native source files pack referenced image pixels, and both GLBs embed their textures. The final family archive must include the listed shared dependencies at their catalogue-relative paths for offline generator reproduction.
