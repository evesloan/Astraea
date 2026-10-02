# Collection structure: independent components

Three new reusable components for the Astraea catalogue: a 2.40 m straight collection bay, a 90° curved return with 1.80 m path radius, and a fully closed terminal. These are authored component assets, not reconstructed original ship content. The 3.40 m nominal height is a component dimension only.

The low, eased plinth, supported shelf noses, shaped timber load frames, deep timber soffit and ivory coved canopy are one continuous cross-section language. Curved boards and overhead profiles follow the same arc. The terminal closes the full silhouette and carries shelf-height metal datums into its timber end field. The terminal has real closed caps, and its field and rails overlap their supporting material by 3 mm and 1 mm respectively.

## Files and reuse

- `source/AST-LIB-STR-001.blend`: editable straight bay
- `source/AST-LIB-STR-002.blend`: editable curved return
- `source/AST-LIB-STR-003.blend`: editable closed terminal
- `source/build_library_structure.py`: disclosed original script-assisted authoring, retained profiles and named parts
- `exports/*.glb`: evaluated geometry, grouped by shared semantic material role
- `stock_anchors.json`: centre-base stock anchors, exact stock bounds, tangent frames, shelf-top polygons and proposed instance placement
- `collision_proposals.json`: separate numeric component hull proposals, never an automatic convex hull spanning the room or approach
- `manifest.json`: dimensions, source/export hashes, semantic parts, pivots, joins, counts and limitations

The authoring script reads `../../standards/materials.py` relative to this asset folder and the catalogue’s existing materials-02 texture set without changing them. The `.blend` files have packed textures. The GLBs embed ordinary 256 px material textures and do not depend on the reference PNGs at runtime.

Rebuild from the catalogue tree with Blender 4.3.2:

`blender -b --threads 2 --python assets/library_structure/source/build_library_structure.py`

## Interfaces

Blender source: metres, Z up, X along the straight collection, front −Y. GLB uses the standard glTF Y-up conversion. Objects have positive unit scale. The architecture pivot is the floor-height start seam, not the centre of its bounding box. Both join caps are inset 1 mm from their nominal seam planes; adjoining components therefore have a 2 mm design gap.

The straight bay ends at `(2.4, 0, 0)`. The curve begins tangent +X, turns counterclockwise and ends at `(1.8, 1.8, 0)` tangent +Y. A demonstrated three-piece arrangement uses straight at the origin, curve at `(2.4, 0, 0)`, and terminal at `(4.2, 1.8, 0)` rotated +90° around Z. Repetition or this inspection arrangement is not a fourth asset.

Shelf tops are Z = 0.30, 0.68, 1.06, 1.44, 1.82, 2.20 and 2.58 m. Between shelves, 0.328 m clear height accommodates the 0.29 m nominal stock height. Every stock anchor uses the centre of its footprint at the exact shelf top, with local bounds `(−.34, −.12, 0)` to `(.34, .12, .29)`. There are 21 anchors each on the straight and curved components; the terminal has none. Curved stock follows the local tangent at 15°, 45° and 75°. Its nominal footprint corners lie more than 45 mm inside a conservative outer shelf chord. Actual exported shelf support, stock bounds and seam checks are supplied in the batch’s independent review.

Upper rows at 1.82 m and above need staff access planning when integrated. The files do not promise standing guest reach to every collection. Stock remains an independent asset instantiated for inspection, never baked into these three structure assets.

The shelter extends 1.015 m forward from the back datum. Its open-span soffit is no lower than 3.025 m. The shaped support underside forward of the 0.445 m plinth projection remains above a conservative local Z = 2.835 m. Those are geometric component envelopes, not proof of headroom in the unavailable original room.

## Counts and evidence

Structural evaluated triangles: straight 1,384; curve 5,498; terminal 520; total 7,402. Each structure has two exported material-role meshes except the three-role terminal. Stock density adds separate instance geometry and is reported with the actual inspected arrangement.

The final fully stocked proof uses 14 instances each of the base upright grouping, reordered grouping and shorter grouping with a flat pair. The three structural pieces plus these 42 stock groups total 37,978 triangles. The ordinary standing view also reuses one batch02 shared table, one batch01 chair and the folio, for 44,394 visible asset triangles. These are observed component geometry figures, not measured native performance. Derived book arrangements are reuse recipes, not additional unique authored assets.

In the standing inspection arrangement, the table is at `(1.20, −2.70, 0)`. Its approved +Y chair candidate is at `(0.65, −1.665, 0)`, yaw 0°, and its optional folio mount is at `(1.20, −2.50, .75)`, yaw 0°. The chair’s measured rear is Y = −1.182708 m, leaving 0.737708 m to the nearest shelving plinth at Y = −0.445 m. This is a measured component gap only; movement, access and original room integration remain untested.

All source parts retain editable geometry and useful bevel/weighted-normal modifiers. Source and export UVs use real metric unwraps, including end caps. Runtime UV layer names are normalized before joining by material role. Any small evaluated bevel UV collapse receives a metric planar repair before export. Byte-level GLB checks verify finite geometry, positive transforms, normals, winding, texture references and nonzero UV triangle area.

`qa/render_imported.py` creates inspection views from the actual GLBs, importing the book group once and making linked mesh/material instances. Neutral and ordinary-height 640×360 views plus 1280 px join/terminal details are labelled Blender component evidence. They are not Godot, original-room, controller, rig, physics, streaming, audio, save or target-PC performance acceptance.
