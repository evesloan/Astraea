# Batch04 independent review

**PASS as a bounded Blender botanical component baseline.** Six original designs and one same-design reflected start closure are ready for the lead's catalogue freeze, restore verification and durable backup. The visible soil pattern defect was corrected and its final exported appearance was rechecked. No high-impact component defect remains. This is not game acceptance: the original project is unavailable.

## Inspected scope

Inspected the actual pixels of the atrium botanical reference and both intimate/dense residential references, the six editable `.blend` sources, seven actual binary GLB exports, labelled imported-GLB render proofs, final botanical texture pixels, material use, source support geometry and composed seat/plant arrangement. All read-only Blender reloads succeeded and did not change sources. No heavy render was launched by the independent reviewer.

| Design | Final triangles | Editable source parts | Export size in metres, XYZ |
|---|---:|---:|---|
| AST-BOT-001 small branching canopy | 7,096 | 305 | 2.394 × 2.006 × 2.693 |
| AST-BOT-002 cupped broad-leaf understory | 1,508 | 33 | 1.011 × 0.701 × 0.926 |
| AST-BOT-003 flowering rosette | 1,520 | 40 | 0.546 × 0.514 × 0.338 |
| AST-BOT-004 straight planted seat | 1,136 | 18 | 2.398 × 1.527 × 0.470 |
| AST-BOT-005 quarter-turn planted seat | 5,364 | 20 | 1.889 × 1.889 × 0.470 |
| AST-BOT-006 closed terminal | 948 | 16 | 0.238 × 1.527 × 0.470 |

The six designs total **17,572 triangles**. AST-BOT-006_START adds 948 triangles when instanced in the demonstration, for 18,520, and is not counted as another original design. Source and export triangle counts, hashes and dimensions match the current manifests. The reflected closure uses baked geometry and positive node transforms.

## Geometry and material evidence

Actual GLB parsing found finite positions/normals/UVs, positive transforms, embedded textures, no degenerate triangles, no opposed normal/winding triangles and no collapsed texture-UV triangles. Used embedded export images match current source texture files. The six new botanical texture files are 256px RGB with no alpha channel. Every exported material is OPAQUE with alpha factor 1. Leaf and petal materials are double-sided; intentional open thin boundaries are documented. Bark and soil are single-sided. Existing architectural material roles retain their earlier double-sided setting.

The canopy keeps 242 editable curve paths and 63 leaf groups. Independent evaluated-source checks verified 241 child branch/support starts inside their actual parent solids and 210 actual petiole endpoints on leaf surfaces. Broad-leaf and rosette attachments add 22 and 36 checked joints. Planter shoe/bracket, bracket/ribbon, rail/ribbon and soil/base/wall checks add 47 measured relationships. Source supports are closed after the documented 1µm cap-vertex weld used to interpret coincident curve-cap vertices. Leaves remain intentionally open.

The terminal and reflected terminal enamel consolidation each has 17 edges with more than two incidences after positional welding because separate closed coping-return parts share/intersect geometry. Every corresponding editable solid is closed; these are component assemblies, not watertight Boolean unions. Fixed terminal detail views show no visible surface artifact. This is not a collision-mesh certification.

Fifteen actual exported material profiles match across the three mating joins, including the start cap. Axial gaps are 2mm to floating-point tolerance, and maximum cross-profile vertex discrepancy is below 0.000001m. Soil is Z0.390, the seat top is Z0.470, bracket/seat bearing is Z0.415, shoe/bracket bearing is Z0.065 and floor contact is Z0.

## Visual and use review

All final canopy and understory proofs show distinct shaped leaf silhouettes, visible connected stems, readable branch hierarchy and grounded bases. The sparse canopy is a deliberately pruned small specimen, not a dense crown or copied monumental atrium tree. The planter forms have usable broad timber ribbons, continuous corner transitions, readable supports and closed end returns.

Initial soil detail contained periodic diagonal bands and colored flecks. Final planter standing/detail renders and the final combined arrangement show neutral earth mottling instead. Old images are retained under the author's `revision01_original_soil` path and are accepted only as unchanged geometry/end-detail evidence. Their old material appearance is not final. Three plant sources retain an unused historical packed soil image; no mesh or curve surface uses it. All used source materials match the current texture library.

Inspected final combined standing Z1.65m, seated observer Z1.19m, actual proposed bench-eye glance and high detail overview pixels. Full views frame the complete assembly. The bench glance intentionally crops nearby foliage and seat pieces; it is clearly separate from the full-object evidence. Raw normal-height viewports are 640×360; the combined labelled copies add separate caption bands.

A second, independent NumPy triangle-intersection implementation confirmed all three root pivots and **115 actual root-base vertices** rest on the exported soil surface. It found the intended seat at Z0.470, all 28 sampled outward rays from the proposed seated eye clear for 8m, a positive control ray hitting real plant geometry, and conservative separation of the proposed 1.6m × 1.2m approach region from every asset. The arrangement gives a legible stopping place, tree hierarchy and an open outlook. Sparse test planting demonstrates components, not a completed inhabited court.

## Boundaries and disposition

Opaque leaves avoid alpha blending/cutout dependence, but still create opaque overdraw and double-sided work. No runtime render budget, target-PC performance, native collision, actor contact, all-species seat compatibility, structural load, real-room ceiling fit or finished-room claim is made. The placed canopy reaches approximately 3.083m above the inspection floor.

Collision records are numeric proposals: eight narrow trunk capsules, optional small basal cylinders and segmented per-part planter hulls. There is no whole-foliage canopy blocker. Curved planter hulls are split into 18 segments per curved strip. Physics and navigation require later engine-side evaluation.

All **358 prior asset/material/standard files** in the independent guard remain byte-identical. The reviewer changed only `qa/batch04/independent_*` files. Current final source/export hashes are in `independent_reviewed_assets_sha256.json`; the broader reviewed-evidence hash list is `independent_reviewed_files.json`. The lead still owns catalogue counter updates, full archive freeze/restore verification and durable backup.

Machine-readable support: `independent_manifest_checks.json`, `independent_glb_report.json`, `independent_actual_support_relationships.json`, `independent_actual_seams.json`, `independent_source_material_usage.json`, `independent_composition_geometry.json`, `independent_visual_review.json`, `independent_render_provenance.json`, `independent_collision_proposals.json`, and `independent_prior_batch_stability.json`.
