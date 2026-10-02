# Aquatic coping, drains and compact entry

Three original script-assisted editable designs: AST-AQU-003 straight coping/drain, AST-AQU-004 compatible curved coping/drain, AST-AQU-005 four-riser entry. START/END pieces are reflected same-profile closure derivatives, not new artistic designs. The original aquatic reference was inspected as pixels before authoring: formed warm ivory pool edges, slim rails, useful dry/wet boundaries and restrained dark grip details inform these components. No district, slide, water surface or physics was created.

## Dimensions and installation proposal

All source geometry is metres/Z up; GLB performs standard Y-up conversion. Coping has deck top Z 0, dry side −Y, water side +Y,1.20 m seam pitch,720 mm total profile,55 mm bullnose,20 real drain slats at 60 mm pitch and 22 mm gaps. Four closed strips frame a 120 × 80 mm open underside drain throat. Two shaped brackets join both apron and nose, while short pads support the drain floor. Coupling tongues below the apron extend23 mm into the next module or the 28 mm terminal, leaving5 mm inside a closed end.

The curve uses the identical profile and a 3 m centreline radius with 1.20 m arc length (22.9183 degrees). Place each next origin at the previous end seam and rotate to its tangent. All role-consolidated GLBs retain positive unit transforms. The START derivative is already X-reflected in source and needs no runtime mirror.

Entry datum is the first descent at(0,0,0). Its 1.40 m opening has 640 mm dry arrival behindY 0, four 180 mm descents and three 320 mm intervening treads, then a 620 mm lower landing atZ −0.72.44 mm returned rails have 1.18 m clear space between them. Dark grip inserts sit flush in actual 4 mm rebates, with shaped bullnoses at tread fronts. Two closed stringers and thin stepped side closures connect trays while retaining the open underside. Upper bearing pads receive atZ −0.18; lower pads atZ −0.86. This is a compact upright/humanoid-scale proposal, not an all-species fit, accessible route or code/load/slip certification.

[interfaces.json](interfaces.json) gives exact shoulder placements, cap paths and actual source-world host-pad bounds. The main dry QA slab ends at the arrival rearY −0.64 insideX ±0.70; the receiving shelves meet only the actual upper pads. A slab must not span the descent. Lower supports meet individual bearing pads; a separate floor may meet the landing toeY 1.58 atZ −0.72.

## Edit, inspect and exchange

Rebuild with Blender 4.3.2: `blender -b --threads 2 --python assets/aquatic_edges/source/build_aquatic_edges.py`. Editable semantic mesh parts and restrained bevels remain in the five source .blend files. Exports consolidate evaluated geometry by five shared roles: warm_stone on foot-contact surfaces and bullnose, aquatic_edge_tile on subordinate apron/side returns, aquatic_satin_alloy, aquatic_dark_grip and ivory_enamel (terminal uses four). Every active UV layer is normalized before joins; embedded ordinary 256 px color maps require no new shader.

Manifests contain measured bounds/triangles, seams, support contacts, rail paths, material/source hashes and limitations. Separate collision proposals use component boxes/profile sweeps and narrow rail capsules. Do not use a whole-assembly convex hull: preserve drain slots/throat, stair underside and hand spaces. These are proposed colliders only.

`qa/render_imported.py -- --preflight-only` reloads sources and verifies cameras cheaply. Final render mode imports the actual GLBs, uses EEVEE_NEXT, 48 samples with no denoiser, and writes 640×360 full/standing views and construction details. All plinths, receiving pads, levels, lighting and cameras are labelled QA_ONLY and are excluded from delivered source assets. There is no simulated water and no engine/actor/target-PC test.

## Corrected source defect

Initial concave side-cheek and terminal-return profiles crossed their lower diagonals, creating broad reversed cap triangles despite closed source edge topology. The underlying outlines were corrected before pixel evidence. Redundant collinear cheek contour points were also removed. Initial independent numerical evidence remains in the batch review folder; final evidence refers to the final source/export hashes.

## Final material correction

Imported pixels exposed excessive teal on all contact planes. The final exports keep the geometry/interfaces unchanged and use warm stone on coping bullnose, landings and treads, with teal limited to the rear apron and thin side returns. Six meaningful final views were refreshed. The initial eight views, including unchanged-geometry underside evidence, remain in `qa/before_warm_contact_revision/` with their exact earlier source/GLB hashes. They are explicitly earlier material evidence, not relabelled as current exports.

A final entry detail pass exposed stringer knees protruding through riser fronts. The knee transitions now finish inside the corresponding closed risers. The support plateaus, host pads, rails, dimensions and triangle count remain unchanged. Earlier finish captures retain their own provenance in `qa/before_recessed_stringer_knees/`; the final three entry views show the corrected construction.
