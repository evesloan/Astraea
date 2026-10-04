# D09 threshold and quiet return components

Three original adjustable designs for the historically documented D09 salon. These are new catalogue sources, not recovered originals, an installed room or a replacement ship layout. The final guest polygon and every real moving-door interface remain unknown.

| ID | Design | Actual source envelope, metres |
|---|---|---|
| AST-SAL-001 | Deep ivory portal return | 5.28 × 1.28 × 3.56 |
| AST-SAL-002 | Rising cove and rib transition | 2.40 × 1.28 × 0.89; underside rises from Z2.85 to Z3.28 |
| AST-SAL-003 | Acoustic book and seat return | 6.20 × 3.20 × 3.74 |

The portal is a separate arrival profile. Its proposed clear rectangle is 4.40m wide and 3.10m high. The 0.14m inner corner arcs begin at Z3.10, centred at source X±2.06/Z3.10, and rise to a Z3.24 crown; they add headroom above that minimum rectangle. No door leaves, cassette fits or unknown mechanism reservations have been authored.

The rising cove belongs inside the quiet return. Place SAL002 at **(-3.10,0,0)** in the SAL003 source frame. SAL003 reserves only the overhead volume X−3.10..−0.70 / Y0..1.28 / Z2.85..3.74 for it. The remaining rear wall/ceiling and high front header meet its rear and high end faces. SAL003 owns the outer structural bearing rib, floor/book foot, useful shelves, shaped seat plinth and pads below that volume. The two-piece union stays inside 6.20 × 3.20 × 3.74m; the historical 7.20 × 5.40 × 3.80m authoring maximum is not measured host geometry.

Source axes are metres, +X right, +Z up and −Y guest/use front. All three origins project to floor Z0; SAL002 is deliberately an overhead component, with no implied floor contact. Standard glTF conversion is source(x,y,z) → native(x,z,−y). The actual node hierarchy is authoritative. `DATUM_` nodes in the GLBs distinguish physical surfaces/contacts from empty poses. Each physical marker names its editable source part. Surface normals and fixture aim directions are separately declared.

The paired quiet section uses a continuous rear wall/cove, articulated ivory ribs, acoustic fields, a shaped recessed bench support, crowned woven pads, tactile walnut shelf/arm landings and restrained champagne joints. Bookshelves are empty production geometry. No existing books, plants, seats, controllers or lighting systems are implicit dependencies. Small opaque fixture lenses have no emission or runtime lights. Three divided pads do not establish registered capacity or universal species fit.

## Rebuild and evidence

Use Blender 4.3.2:

`blender --background --threads 2 --python-exit-code 1 --python assets/salon_threshold/source/build_salon_threshold.py`

The generator creates all output directories, retains semantic source meshes and ordinary material roles, normalizes active metric UV-layer names before static export consolidation, packs source textures and embeds the used textures in each GLB. `dependency_manifest.json` gives the complete material-helper input closure, including the otherwise unused PNG that the helper loads. `qa/salon_threshold_source_only.zip` contains inputs only; `qa/source_only_rebuild.json` verifies an output-free rebuild invoked from /tmp and byte-identical GLBs.

`collision_proposals.json` keeps modest structural compounds: 11 portal, 8 rising-cove and 30 quiet hulls, reduced from the first finish-by-finish proposals of 247, 16 and 115. Attached finish layers and small recesses share occupied structural envelopes; storage boards/cheeks stay distinct to preserve shelf voids. The stated **18mm** allowance applies specifically to the four-facet **exterior** approximation; it is not a global collision-error or clearance bound. The [independent curved-profile probes](../../qa/batch10/independent_profile_collision.json) measured three separate inward allowances: up to **11.774mm** loss of local portal crown clearance, **4.023mm** below the visible cove underside, and **47.023mm** in the shallow finish channel that the structural compound intentionally fills. The first two are conservative clearance reductions; the channel fill is deliberate simplification of a recess. Therefore “space below the lower profile” in the cove proposal means usable space subject to the measured 4.023mm allowance, not exact coincidence with the visual underside. The exterior approximation and these three measured scopes must remain distinct when choosing final collision margins; none establishes host, moving-door, actor or cart fit. Finite empty portal, quiet approach and book-shelf regions are declared in both coordinate frames. The 561 clear/blocked samples do not establish real actor/cart routes. `qa/glb_independent_validation.json` checks actual binary meshes, normals, dimensions, UV area, embedded texture hashes and marker positions. `qa/source_reload_checks.json` checks editable sources. Imported-GLB images and their exact hashes/cameras are recorded in `qa/render_evidence.json`; cutaway operations are explicitly QA only, and open uncapped cut faces are not construction cavities.

The final ship adoption gate still needs recovered host geometry, actual moving-door sweeps, real placement, actor/cart routes, registered use slots, structural/support assessment and engine-side lighting/render/performance review.
