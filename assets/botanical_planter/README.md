# Planted-seat architecture — Blender component catalogue

Three original joined designs: AST-BOT-004 straight, AST-BOT-005 quarter-turn, AST-BOT-006 closed terminal. These are new component assets; they do not reconstruct or modify the unavailable game or certify room, actor, engine, physics, structural loading or ceiling fit.

The family transfers the references' inhabited planted edge at human scale. The sculpted stone basin has actual separate walls and a recessed cavity base. Ivory enamel coping joins the rear of three thick walnut seating ribbons. Two continuous timber rails and shaped enamel brackets carry the ribbons into floor-contact stone shoes. The bed is deliberately behind the sitting edge; a 0.17 m plan gap separates the back of the timber from the usable soil face. There is no giant box under the whole canopy or bench.

## Dimensions and joins

All values are metres; Blender Z up, front -Y, floor Z0. Pivot is the nominal start seam. Soil is Z0.390, timber seat top Z0.470, timber underside Z0.415, coping Z0.430. Soil depth is 0.285 above the cavity base at Z0.105.

| Design | Overall dimensions XYZ | Evaluated triangles | Nominal connection |
|---|---:|---:|---|
| AST-BOT-004 straight | 2.398 × 1.52659 × 0.470 | 1,136 | (0,0,0) to (2.4,0,0), yaw0 |
| AST-BOT-005 quarter-turn | 1.88897 × 1.88897 × 0.470 | 5,364 | (0,0,0) to (1.4,1.4,0), outgoing yaw90 |
| AST-BOT-006 terminal | 0.238 × 1.52659 × 0.470 | 948 | Start seam only; basin end closes at local X0.160 |

Each joined seam has a deliberate 2 mm air gap. The profile extends from Y−0.490 seating nose to approximately Y+1.037 rear coping. Straight soil opening is X0.001..2.399, Y0.150..0.880. Curved opening follows an annulus centered at (0,1.4), radii0.520..1.250; maximum facet step is5°. Full detail is in each manifest.

Place straight at (0,0,0), quarter at (2.4,0,0), terminal at (3.8,1.4,0) with yaw90°. To close the first end, use derived/AST-BOT-006_START.glb at (0,0,0), yaw0°. That is the same terminal design reflected on mesh X, with corrected normals and positive identity transforms; it is not a fourth authored asset. A180° instance rotation would incorrectly swap seat and soil sides, so use the baked variant. Its source recipe and numeric mirrored collision proposal are included.

## Files and reproducibility

The three root .blend files retain named semantic mesh parts and editable easing/normal modifiers. Run source/build_botanical_planter.py with Blender4.3.2 to rebuild the main assets, then source/build_start_closure.py for the optional mirrored closure. Guest material roles are reused without editing the shared library; botanical_soil comes from the new botanical library. All referenced texture images are packed in .blend and embedded in the GLB.

Each final GLB consolidates evaluated copies into five semantic role meshes: warm_stone, ivory_enamel, warm_walnut, champagne_metal and botanical_soil. UV layers are normalized before joining. Longitudinal wood grain follows each straight or curved ribbon. Finite geometry, normal direction, actual embedded image hashes, dimensions and nonzero UV surface area are checked from the binary GLB.

## Evidence and limits

qa/check_relationships.py measures actual evaluated shoe/bracket/seat contact patch intersections and verifies source seam sections. Every bracket contacts all three timber ribbons; soil volume contacts the cavity base; shoes reach Z0. qa/measured_relationships.json records the measured results. These are geometry checks, not mechanical load calculations or game physics.

qa/render_imported.py reloads the sources and imports the final GLBs. Its full views use standards/qa_frame.py before EEVEE_NEXT rendering, with denoising disabled. Evidence consists of a640px three-quarter view, ordinary standing eyeZ1.65, ordinary seated eyeZ1.15, and construction details. All proofs are labelled Blender component QA. The lead's separate botanical arrangement combines these edges with the new plant assets; the empty-planter proofs here focus on construction.

collision_proposals.json splits walls, seat ribbons, soil support volumes and individual brackets into numeric hull proposals, preserving the open basin and approach above soil. It does not add runtime collisions or block an entire foliage canopy. The1.2 m front approach is an unoccupied geometric proposal only. Plant overlap and leaf/seat separation must be checked for each chosen composition.

### Soil texture review revision

The initial five imported-GLB views and their exact source/export hashes are preserved in qa/revision01_original_soil, along with superseded packed-source backups. Independent pixel review identified diagonal waves and coloured specks in the original new soil texture. The lead corrected only botanical_soil to darker, low-contrast non-directional earth. source/repack_soil.py repacked the corrected soil and re-exported the same geometry; it asserts unchanged source vertex positions. All current GLBs pass the binary/material/UV/contact checks again. The current qa/joined_standing_640 and qa/seat_soil_support_detail_1280 proofs show the corrected soil. The initial three-quarter, seated and terminal views document unchanged architecture with their explicitly older soil hashes; the lead also captures the final combined botanical arrangement at seated height.

The returned terminal coping intentionally meets/intersects adjoining closed solids. Each editable source solid is closed; role-consolidated exports are component assemblies, not a single watertight Boolean union. Independent review found no visible terminal seam artifact in the inspected views.
