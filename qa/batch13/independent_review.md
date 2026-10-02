# Batch13 independent component review

**Accept the four authored designs as bounded editable component work.** The proposed interface index has 69 designs; canonical catalogue/index promotion remains the lead’s action. This review did not modify authored assets, shared standards, either canonical index, or any protected historical file.

The three actual reference images and earlier accepted botanical exports were inspected. Their useful direction is layered planting around a resting edge with a clear view gap. The final partial edge expresses that direction through a fan crown, unequal rearward trailing stems, and three independently rooted flowering clumps. It does not reconstruct the reference courtyard or supply missing ship geometry.

## Final authored and native geometry

| Design | Editable mesh parts | Actual GLB triangles | GLB mesh nodes/primitives | Materials | Two-sided materials | Two-sided triangles | Collision proposals |
|---|---:|---:|---:|---:|---:|---:|---:|
| AST-BOT-007 fan crown | 22 | 1,130 | 4 | 4 | 3 | 882 | 11 |
| AST-BOT-008 trailing cluster | 56 | 1,256 | 4 | 4 | 3 | 1,200 | 2 |
| AST-BOT-009 flowering bank | 114 | 2,448 | 5 | 5 | 4 | 2,280 | 6 |
| AST-BOT-010 raised end | 28 | 1,806 | 5 | 5 | 4 | 1,782 | 25 |

The total is 6,640 triangles and 18 role-consolidated mesh primitives across four GLBs. All materials are opaque; there are no alpha cards, native animations or skins. Counts describe actual files, not renderer draws, batching behavior, memory use or target-PC performance. Source semantic parts remain editable. Intentionally open folded leaves/petals are two-sided and decorative/noncolliding. Shared original material inputs remain unchanged.

Independent source reloads and native hierarchy parsing agree in bounds, evaluated geometry, material roles and embedded texture bytes. Per-material position/UV/split-normal corner comparisons also pass. Positions and UVs use 1e-6 tolerance; exported split-normal components use 2e-4 tolerance (observed attribute-vector differences below 8.3e-5). For010, the final source/export manifests and independent evaluated-source inspection agree on three repaired bevel polygons (front wall37/40, rear wall40). Applying the stated dominant-plane projection yields matching actual native attributes. The earlier four-polygon count belonged to a superseded initial build. Raw source and export UVs are not claimed to be identical everywhere.

Every physical marker has a named source surface and actual native mesh/normal witness. Every botanical attachment is checked against real triangles and a complete support graph.009 legitimately has three root-connected groups, each with a physical soil contact; it has no decorative crossbar connecting the clumps. The raised end’s complete 28-part graph reaches its floor-contact structure. Mating markers alone do not establish these results.

## Useful spaces and real interfaces

- Six actual native surface witnesses across existing004 and new010 confirm the original `planted_seat_470_soil_390` start profile, opposed normals and nominal2mm joint
- The sitting ribbon retains its470mm depth/top datum. Both soil cells, supported upper slab/piers, closed terminal and under-seat bays are real geometry
- Whole inset boxes and positive/negative probes preserve the soil structural cavities, under-seat bays, full seated space, front approach and standalone rear approach. Soil medium is explicitly excluded only when testing the structural planting cavity; it is not falsely called an empty visual volume
- In the actual joined placement, all three root reservations fit the real soil polygons. Proposed spatial depth reservations fit the285mm lower and425mm upper soil depths. Below-soil roots remain unmodelled; these numbers do not establish viability or growth
- Exact clipping of the actual trailing triangles over the rear coping footprint gives127.600mm minimum vertical clearance. The full trailing geometry drops570.972mm below its soil datum and remains behind the seating
- Three complete joined clear boxes and nine proposed seated sightlines pass independently, with blocked seat/riser/terminal/stem controls and75 clear probes that an incorrect whole-arrangement hull would block
-007’s actual lowest foliage is1.230m above soil (1.620m in this placement), so no universal headroom is claimed

## Bounded collision and finish limits

The initial rear-wall convex proposal invaded otherwise clear soil cavities. Profile splitting fixed that without reducing the usable730mm soil width. The initial raised coping entered the sitting field; its real profile moved rearward while the full seat remained useful. A visible flowering-bank connector was removed in favor of legitimate independently rooted groups. Exposed terminal finish coincidences were corrected with a3mm stone setback and deliberate trim terminations.

Final010 proposal error remains explicit. A35mm maximum-edge surface sample finds19.543mm external inflation at the local lower bracket/shoe compound. Continuous polygon clipping finds0.000154325m² front-wall and0.060627380m² rear-wall surface area outside the compound union; sampled distance of those gaps is only0.254mm and0.301mm respectively. Thus complete surface coverage is **not** claimed. Finite samples do not certify a continuous maximum error. All stated useful-volume regressions pass. These compounds remain unadopted proposals.

The final axial finish screen finds no new exposed terminal cross-material overlap. Six same-facing overlaps are buried bearing contacts; three start-end slices retain the accepted mating profile atX0.001. Those inherited construction slices are disclosed, not hidden by a visibility flag. The advisory screen does not prove every nonaxial surface or future placement.

## Actual pixels and frozen scope

All four final imported joined images in `assembly/r06` were inspected: standing at1.65m, seated outlook at1.19m, rear maintenance at1.65m, and the deliberate seam/detail crop. Six additional component images were inspected. Distinct forms, support, soil steps, rear tails and a usable seat read at640×360. The seated image deliberately opens onto a mostly blank QA studio field; it does not show a recovered receiving garden.007’s2.35m orthographic view is a specimen view, with ordinary-height evidence supplied by the joined capture.

The final010 manifest has eleven evidence-only changes after capture. The original capture JSON and exact captured manifest are preserved. `independent_visual_review.json` and the lead’s `assembly/r06/post_capture_metadata_amendment.json` separately bind the current manifest, unchanged source/GLB and the original image scope. No rerender of unchanged geometry is inferred.

## Rebuild, preservation and index

Reviewer-controlled fresh stages seeded9 production inputs for the plants and20 for the transition, including every original helper-loaded material role. All four fresh GLBs are byte-identical. Independently reloaded editable topology/UV/material/hierarchy/modifier/property signatures and evaluated source geometry match. Python open attempts and actual native-loaded Blender image datablocks are recorded. OS ptrace tracing was unavailable; no system-call-complete trace is claimed. Initial failed instrumentation attempts and superseded revisions remain as historical evidence.

The final rebuild receipts are `independent_rebuild_botanical_cluster_r02.json` and `independent_rebuild_botanical_transition_r04.json`. The exact r04 runner is preserved as `independent_rebuild_runner_executed_transition_r04.py`; later runner adjustment merely recognizes newly generated cluster manifests reopened for hashing. No old asset output or QA input was seeded into either successful fresh stage.

All1,834 protected file hashes match the supplied baseline. Every prior65 catalogue and canonical interface record retains exact raw JSON bytes and decoded objects. The proposal `independent_interface_normalized_index_proposed.json` preserves those65 records verbatim and adds exactly four. Its207 source/export/manifest bindings are current. Canonical indices remain untouched by this reviewer.

**Unvalidated:** host/ship allocation, deck voids, installed floor support, actor/cart/species fit, horticulture/root growth, structural loads, irrigation, wind, engine adoption, collision behavior, LOD, and target-PC performance. No new design is counted for the reused004/006_START context, QA floor/cameras, source snapshots, textures, or rebuild copies. There is no reason to broaden this batch before its lead freeze/restore/backup gate.
