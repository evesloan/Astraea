# Staff wall / cart protection — three independent designs

Original script-assisted Blender construction, 2 October 2026. These are catalogue components, not a reconstructed room or missing ship. The two supplied staff-corridor photographs and the shared-staff-room photograph were opened and visually inspected before authoring. Their washable panels, exposed practical construction, ordinary fixing details and service protection inform this family; their narrow circulation, bunks and capacity are not copied.

## Contents and interfaces

| ID | Component | Overall Blender dimensions | Evaluated triangles |
| --- | --- | --- | --- |
| AST-STF-001 | Washable panel / rubber bumper bay | 1.200 × 0.120 × 2.600 m | See manifest |
| AST-STF-002 | Continuous inside-corner return | 0.300 × 0.300 × 2.600 m | See manifest |
| AST-STF-003 | Closed bumper / folded edge terminal | 0.090 × 0.120 × 2.600 m | See manifest |

All geometry is metric, Z up. The usual front is −Y. GLBs use the standard glTF Y-up conversion. Each asset has an editable .blend, portable embedded-texture GLB, detailed manifest and separate compound collision proposal. Three source designs only; repeated placements do not add new designs.

- Bay origin: left floor seam. Backing is exactly Y0; seam planes are X0 and X1.2. Rubber projects to Y−0.120. Cladding ends Z2.600; it does not declare the height of a real room.
- Panels stop 6 mm short of installation seams: two mating pieces have a 12 mm reveal. Bumper, floor cove and top return meet on the exact seam plane with no visible-profile gap. Each individual extrusion is capped for independent use.
- Corner origin: intersection of backing X0/Y0 at the floor. Its occupied face quadrant is X>0, Y<0. A leg ends X0.300 and accepts a bay at (0.300,0,0), rotation0°. B leg ends Y−0.300 and accepts a bay at (0,−1.500,0), rotation+90°. Both faces use the same 120 mm inward bumper projection; the continuous miter avoids overlapping full wall boxes.
- Terminal origin: inboard seam X0. Place at a bay’s right seam. It adds 90 mm in X, with an actual 2 mm folded end sheet, 16 mm return flanges, closed cove plate and a tapered solid rubber cap ending X0.090. The generator does not add a doorway or sliding pocket.
- Backing carriers must be fixed to separately verified substrate planes. The coved formed foot reaches Z0. These parts are not a freestanding wall structure.

The inside-corner cove, guard and cap profiles are matching continuous geometry. Actual exported seam checks are in qa/connection_validation.json. All source semantic meshes are closed/manifold with positive signed volume. Material-role export consolidation follows active UV normalization; UVs retain metric scale, including the capped ends. Shared staff_white_paint, staff_zinc and staff_rubber use original packed color tiles. None of the guest material definitions are edited.

## Rebuild and inspect

From the catalogue root, run Blender 4.3.2:

    blender --background --threads 2 --python assets/staff_wall/source/build_staff_wall.py
    python assets/staff_wall/qa/validate_glb.py
    python assets/staff_wall/qa/check_connections.py
    blender --background --threads 4 --python assets/staff_wall/qa/render_imported.py

Dependencies are standards/staff_materials.py, materials/staff/ and standards/qa_frame.py for camera evidence. Source blend files pack the material images and stay independently editable. GLBs embed all texture bytes. The Python generator retains named semantic parts and editable formed-edge bevel / weighted-normal modifiers; exported meshes evaluate those modifiers and consolidate static parts into three semantic material groups.

The GLB validator independently parses binary accessors, verifies source/export dimensions, finite geometry, nondegenerate UV surface, winding/normal agreement, unapplied scale and byte-identical embedded color maps. Source reload validation checks closed manifold components and positive volume. Compound collision files are conservative proposals only; their boxes preserve the usable inside quadrant rather than filling it with one hull.

## Evidence and limits

qa/render_evidence.json stores exact final source/export SHA-256 hashes, instance transforms, camera locations, lens/orthographic values and framing results. All four images were rendered from imported GLBs using verified Eevee with 48 samples and no OIDN, then visually inspected. Labelled copies explicitly identify Blender component evidence.

- joined_full_silhouette_640: all three designs in a joined L arrangement, full conservative bounds pass with 3.5% margin
- joined_eye_height_640: eye at Z1.650 m; the lower foot is intentionally cropped and this is not the complete silhouette view
- corner_bumper_cove_detail_1280: close view of continuous rubber corner, fixings, panel reveals and the upper cove transition; the lowest floor flange is outside this crop
- closed_terminal_detail_1280: the full terminal height, closed rubber cap, folded sheet and complete end of cove

The steel parts are deliberately restrained rather than luxury trim. Pale washable panel faces, dark rubber cart protection, coved feet and ordinary fixings establish a separate staff material language. This evidence does not establish game rendering, CRT appearance, actual route width, actors, contact physics, doors, chores, crew, capacity or performance. Integration into the missing original project remains pending.
