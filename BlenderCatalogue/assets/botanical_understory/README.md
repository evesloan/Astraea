# Original botanical companions

Two original script-assisted designs for the separate Blender asset catalogue. The source `.blend` files preserve editable named meshes. This work does not reconstruct the unavailable original game and makes no native runtime or room-fit claim.

| Catalogue ID | Component | Actual width × depth × height | Evaluated triangles | Editable parts | GLB meshes/primitives |
|---|---|---:|---:|---:|---:|
| AST-BOT-002 | Cupped broad-leaf understory | 1.011 × 0.701 × 0.926 m | 1,508 | 33 | 4 / 4 |
| AST-BOT-003 | Low flowering spoon-leaf rosette | 0.546 × 0.514 × 0.338 m | 1,520 | 40 | 5 / 5 |

The understory has three readable stem routes, ten deliberately varied broad cupped leaves, ten petioles and ten raised midribs. Its long-axis fan was composed to sit within a 0.73 m deep soil opening. The rosette has fifteen spoon leaves in three layers and three restrained, five-petal flower heads on connected stems. Neither uses a sphere mass, alpha card cloud or random arrangement.

## Source and export

- `source/AST-BOT-002.blend`, `source/AST-BOT-003.blend`: editable metre-scale sources, packed texture dependencies, soil plane Z0
- `source/build_botanical_understory.py`: reproducible original authoring generator; requires Blender 4.3.2 and shared `standards/botanical_materials.py`
- `exports/AST-BOT-002.glb`, `exports/AST-BOT-003.glb`: evaluated static exports consolidated by semantic material role, standard glTF Y-up
- Individual `.manifest.json` files and `manifest.json`: exact bounds, roles, joins, provenance and hashes
- `collision_proposals.json`: optional small basal cylinder proposals only; foliage and flower crowns stay out of collision

Leaf UVs follow the shared U-across/V-root-to-tip botanical convention. Tube UVs use surface distance and stem length. Active UV names are normalized before joining export copies. Every used color texture is embedded. All materials are opaque. Leaves and petals intentionally have open boundaries and double-sided materials; stems, crowns and flower receptacles are closed solids.

## Proposed planting relationship

Both origins are the soil plane at root/crown center, local `(0, 0, 0)`. No soil is included in either visual export. In the shared straight planter example, translate a plant to `(1.2, 0.51, 0.390)` metres.

The understory then spans Y 0.1684–0.8691, within the soil opening Y 0.15–0.88, and stays 0.1884 m behind the seat-back datum Y −0.02. The rosette spans Y 0.2479–0.7622 and stays 0.2679 m behind that datum. These are measured component bounds, not seated-actor or comfort acceptance. Leave at least half the actual plant width between its center and a closed soil end; avoid overlapping specimens unless a composed arrangement is intentionally reviewed.

Suggested soil patch/depth data are spatial placeholders only: understory patch radius 0.13 m and depth 0.22 m; rosette patch radius 0.085 m and depth 0.14 m. They are not horticultural or structural certification.

## Evidence and validation

`qa/source_reload_checks.json` records successful source reload, editable part topology, source UV area, exact Z0 contact and attachment checks against actual parent meshes. All listed joints lie inside or on their closed supports. Thin leaf boundaries are intentional.

`qa/glb_validation.json` is an independent binary-accessor GLB audit. Both exports have finite geometry, unit normals, consistent winding, no zero-area triangles, no collapsed UV triangles, embedded textures matching the original shared pixels, positive determinant transforms, and opaque material modes. Runtime mesh/primitive counts are measured, not a draw-call budget guarantee.

`qa/*_labelled.png` and `qa/render_evidence.json` provide actual imported-GLB evidence, including separate 640×360 silhouettes, a 640×360 standing-height comparison, and 1280×960 detail. Rendered with EEVEE_NEXT and no denoising. All full-frame cameras pass `standards/qa_frame.py` conservative framing before rendering. Inspection floor, cameras and lighting are QA aids and absent from the export.

The author inspected all three actual batch04 reference images. The original diorama informed layered planted edges and visible supporting stems; the intimate and dense residential references informed modest scale and views above low foliage. No reference geometry or texture was extracted.
