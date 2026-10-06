# Three-bay spine garden court for suite205

Source-only connected residential court study, 6 October 2026. Game and Catalogue were not written or imported. No structural certification, installed floor, runtime navigation, final art or NPC-use claim is made.

## Editable deliverables
- `source.blend`: authoritative editable source, including retained catalogue mesh and curve parts, packed textures and actual local light objects.
- `source.glb`: world-aligned Y-up exchange. Blender area lights are not supported by GLB; compose from the blend and use `LIGHTS.json`.
- `build_court.py`: deterministic source generator. Run Blender with two threads only after coordinating the shared source slot.
- `PARTS.json`: actual evaluated world bounds, triangles and Blender transforms per source mesh/curve.
- `ASSET_TRANSFORMS.json`: exact reused catalogue assets, placements and unchanged dependency hashes.
- `RETAINED_ASSET_PLACEMENT_CHECKS.json`: all10,171 placed catalogue parts match evaluated retained-source transforms/vertices; all11 original asset dimensions match their catalogue records. This catches misassembly that an export comparison alone cannot.
- `CONTACTS.json`, `ROUTES.json`, `LIGHTS.json`, `TARGET_CONTRACT.json`: explicit source interfaces.
- `GEOMETRY_CHECKS.json` and `EXCHANGE_CHECKS.json`: final scoped checks; scripts reproduce them without Godot.
- `REFERENCE_APPLICATION.json`: exact documents, complete chapters/pages and full images personally inspected, with consequences for this source.
- `retained_r002/` and `retained_r003/`: earlier court revisions used for the parent's first composite view, retained with its original hashes. Their route and unevaluated catalogue-transform findings are historical; the corrected source must be checked against retained-asset matrices, not just its own export.

## Coordinates and composition
Metres. All source geometry uses global Blender `(world X, -world Z, world Y)`. Append it without an additional placement transform. Standard GLB Y-up therefore has the actual ship world coordinates. The parent applies each room's own local-to-world placement separately.

The pilot is existing source205 / AST-UNIT-D14-fbfbe316e3a58c68, with neighbors181/229. This source does not replace their interiors or alter any identity/rest ledger. The parent owns their corrected kitchenette, enclosed bathroom and proposed furniture layout.

The court has a real new garden base at Y84, a spine-side gallery at Y88.5, and level end crosslinks at both levels. Two shaped stopping pockets reach X14.1; the continuous passing route stays on their west side. Lower reading seats face the planted heart. A 26-riser, two-flight stair with an intermediate landing connects the garden and gallery. It has real treads, risers, stringers and bounded edges. Canopy, shrub, flower and groundcover scales come from the actual catalogue. The source has eight chairs, a two-person bench, five shared tables, open folios and book shelves as use proposals; these are not guest-capacity or occupied-NPC claims.

Public lower travel remains west of X25.6; X26–29.05 is a quiet planted setback. No public balcony runs against bedroom glazing. Core walls remain closed. The only level connections are to genuinely open spine segments at Z−333…−330.

An opaque cap and authored local light panels establish an internal garden. No exterior image panel or invented sky view is used. The final maximum Y92.70 leaves 0.06m below a hypothetical D15 0.24m slab underside at92.76. The east header begins at92.42. No new geometry descends below Y78.

## Support and limits
There was no existing court floor. The proposed base, gallery and roof therefore have explicit new supports. Under-garden triangulated transfers touch the actual D12/D13 compiled spine geometry; the D14 crosslink has underside-bearing beams. New gallery columns, short transfer members, stair piers and roof ribs connect the source assemblies.

Those contacts establish geometric continuity only. A 25m transfer is not certified by modeling it. Existing spine slab capacity, anchorage, stiffness, loading, fire and MEP interfaces require structural resolution before adoption. No hidden receiving girder or existing garden slab is claimed.

Two source routes clear conservative 1.75m/1.70m-wide by2.1m-high swept boxes at 20cm spacing. This is not loaded-cart, largest-species, turning, interaction or accessibility approval. The lower garden and upper gallery each have a level crosslink; no new local accessible lift or complete tested interdeck journey is claimed.

The final source has11,294 mesh/curve parts and342,844 evaluated triangles. The exchange has326,644 triangles because its135 canopy leaf-spray nodes consolidate reversed duplicate leaf triangles under double-sided materials. All source geometry node identities and evaluated bounds survive exchange, with a maximum bounds delta recorded in EXCHANGE_CHECKS.json. This is a geometry/bounds check, not an engine import or final visual-equivalence test. The11,294-node source exchange has not been compacted for runtime draw-call/instance budgeting.

The four D12 top receiver shoes occupy the outer0.30m of the positive-X spine edge; the source does not claim an unchanged full-width D12 walking clearance. Their route/anchorage interface remains proposed.

The parent is composing the actual room through its window into this court. Full-aperture seated/standing views with the room frame, furniture, glazing and final renderer remain that separate review gate.
