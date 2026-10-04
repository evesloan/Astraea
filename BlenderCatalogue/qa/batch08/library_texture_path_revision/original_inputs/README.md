# Astraea library contents — two original artistic assets

These are independent catalogue components made while the original game is unavailable. They do not restore that game, establish room fit, or claim engine, actor, interaction or performance acceptance. The four supplied library reference images were visually inspected for collection rhythm and useful reading details; no image pixels, copyrighted book covers, external 3D assets, or Tripo output were used.

## Stable assets and deliberate derived arrangements

- **AST-LIB-006, upright bound collection:** eleven cloth-bound books, ten upright and one leaning into a taller neighbor, with weighted endstops. 802 triangles, 7 ordinary semantic material primitives. Bounds X −.2938668 to .248, Y −.11068 to .11, Z 0 to .278 m. The silhouette, board covers, rounded spine cases, page recesses, raised bands and catalogue labels are real low-poly geometry.
- **AST-LIB-007, open field folio:** an open shaped spread on two closed bound books. 276 triangles, 8 semantic material primitives. Bounds X ±.185, Y −.140 to .116, Z 0 to .0801 m. The frontmost 24 mm is the cloth bookmark. The actual support rectangle is the lower cover, X ±.149 and Y ±.1105 at Z0.
- **AST-LIB-006 reordered assembly:** the same original eleven book designs and stops rearranged, 802 triangles. The leaning contact pair stays together. This is an assembly variation, not a third artistic asset.
- **AST-LIB-006 short-flat assembly:** eight of the same books: five uprights and their leaning companion at left, two existing volumes laid flat at right. 580 triangles. Bounds X −.3338668 to .2805, Y −.11068 to .11, Z 0 to .278 m. Separate collision proposals preserve the deliberate gap. This is an assembly variation, not a fourth artistic asset.

All three upright-stock arrangements fit the centered .68 × .24 × .29 m interface. Rotate around Z as appropriate; Blender front is −Y, exported glTF front is +Z. Each base pivot is at actual support Z0. `stock_assembly_recipes.json` lists exact unchanged constituent-object transforms, selected book IDs, omitted IDs, physical bounds and support records. Alternate the three layouts rather than repeating an identical publisher height sequence on every shelf.

## Editing and reproduction

1. Run `python make_book_textures.py` to reproduce the original 256 px local materials, including the handwritten bitmap alphabet and original field-note/orbital-page layouts. No external font, screenshot or source-image file is needed.
2. Run `blender -b -t 2 --python build_library_contents.py` to produce the two editable `.blend` sources, semantic consolidated GLBs, manifests and collision proposal data.
3. Run `blender -b -t 2 --python build_stock_variants.py` to apply the documented assembly recipes to the reloaded editable upright source and export the two derived GLBs. This generates no new constituent book geometry.
4. Run `python qa/validate_glb.py` and `blender -b -t 2 --python qa/reload_and_render.py` for binary export and paired source/import checks. `-- --render` also produces the labelled review inputs from actual imported GLBs.

Shared `../../standards/materials.py` and `../../materials/` are unchanged revision 02 dependencies. The visible shared role is champagne metal on the bookstops; local book roles describe cloth bindings, paper edges, label stock, printed ink and the two original spread pages. Packed images preserve source portability and exports embed the exact PNG bytes. Metric UVs are normalized to the single active name `UV_Metric_Metres` before consolidation. Folio printed faces intentionally use a single physical page-layout rectangle .171 × .219 m; all page sides and caps retain nonzero metric UV area.

## Placement proposals

Structure shelf centers: X .4 / 1.2 / 2, Y −.2, shelf tops .30 / .68 / 1.06 / 1.44 / 1.82 / 2.20 / 2.58 m. Curved placement follows the structure author's tangent anchors; all group origins remain within the centered stock envelope. Sheltered study shelves: (−.711, .075, .420) and (−.711, .075, .830), Z rotation 90°. Upper collections require staff access planning.

Suggested shared-table folio placement is (0, .20, .750), Z rotation 0°. The study author's four writing rectangles leave a 15 mm X margin beyond this folio. Suggested single-reading placement is (.12, .08, .752), Z rotation 0°. Tabletop contact and closed-stack contact levels are 0 / .026 / .048 m in the asset. Open cover bottoms meet the top closed book at .048 m; leaf blocks meet cover tops at .052 m. Page shoulders reach .0801 m.

Collision JSON files contain numeric static-group proposals only. Individual picking, page turning, actor hands, interactive-volume collisions and runtime material instancing must be handled separately during original-game integration. Do not infer those behaviors from this catalogue.

## Evidence

`qa/glb_independent_validation.json` independently parses every binary GLB and checks geometry, dimensions, triangle counts, material/image references, exact embedded PNG bytes, winding, transforms and nonzero UV triangle area. `qa/source_reload_import_audit.json` reloads both `.blend` sources and imports their actual GLBs. `qa/variant_source_import_audit.json` compares both derived recipes with actual GLB imports. Review images show actual imported GLBs on neutral QA support surfaces at ordinary standing/seated camera heights, with separate detail views. They are Blender component evidence, not game output.
