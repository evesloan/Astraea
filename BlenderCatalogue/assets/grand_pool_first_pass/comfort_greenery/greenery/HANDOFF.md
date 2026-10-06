# Grand Pool comfort greenery: prepared source candidate

Status: deterministic candidate geometry and scripts prepared in scratch. Blender source authoring, evaluated-source QA, rendering, export, catalogue adoption and runtime review have **not run**. The parent controls the next two-thread source slot. Nothing in this package launches Blender automatically.

## Scope and ownership

Prospective target is the new `assets/grand_pool_first_pass/comfort_greenery/greenery` directory. Existing source/export paths and material libraries remain untouched. Six BOT-003 basal banks, six BOT-002 middle banks, six fitted BOT-007 crowns and five BOT-003 wet-pot whorls are 23 separately placed derivatives. Together with the parent's four media assemblies, 51 installed objects and 48 earlier planned additions, the cap remains 126. There are zero new catalogue IDs and no optional wet beds.

Each bank is an explicitly authored multi-root botanical derivative, not a renamed group hiding extra externally placed exports. Internal counts remain visible: nine roots per basal bank; three roots per ordinary middle bank, two for the screen-adjacent middle; one joined crown per fan derivative; one additive sleeve for each wet whorl. All root-connected semantic mesh parts remain editable.

The pure plan has 1,990 editable parts and 77,258 triangles across the 23 placements. Consolidation by existing material role would produce 103 mesh/material groups before any renderer-specific surface accounting. These are measured/planned costs, not a performance acceptance claim.

## Visual construction

- Basal banks deliberately overlap 135 broad spoon leaves per bed in staggered low crowns. Five small folded-flower clusters provide restrained accents. Pure vertical leaf projection covers approximately 75% of the actual soil polygon before the middle/crown layers and retained plants; this is a density aid, not a visual-pass metric.
- Middle banks use substantial, individually cupped and twisted source-derived blades with real closed stems/petioles. Unequal heights bridge low cover to upper crowns.
- Fitted crowns use the source's pleated fan topology, root-to-tip UV intent and closed branching construction. Each fan has its own chosen pitch, azimuth, size and petiole, primarily near-upright so real depth fits. There is no global depth squash and no unchanged oversized BOT-007 placement.
- The first bench's bed has low cover across its complete reservation, while its middle and upper derivatives stay on the east side. The tallest leaf is below the approved 55.20 m cap.
- Wet whorls remain small, coherent potted accents. The additive crown sleeve begins 27 mm above the original root plane; its shared-volume witness is inside the actual retained crown, and every new surface stays above the actual pot's rim top.
- Opaque jade, sage, olive, flower and bark materials are appended from the exact pinned botanical .blend files with their actual packed PNG bytes. No new palette, emission, alpha cards, reference-photo billboards, renderer switch, shared shaders or lighting changes.

## Prepared files and gates

1. `geometry_plan.py` contains the deterministic source-derived construction; `greenery_contract.json` records every local mesh vertex, face, loop UV, shape control, placement, reservation, marker and physical joint.
2. `INPUT_PINS.json` pins original sources/exports, source formula scripts, botanical textures, support/furnishing contracts, audit reservations and archived reference images. `prepare_pins.py` only reads those inputs and writes inside its installed package. The sibling `reference_audit` preserves original audit JSON bytes and exact inspected baseline images; package-relative pin paths survive installation. `REFERENCE_RELOCATION.json` resolves inspected original paths to retained image bytes, so later Game captures cannot invalidate evidence. Geometry planning falls back to the original scratch audit only while the sibling is absent; reference-image pinning requires the archive.
3. `check_contract.py` independently checks count/ownership, reservations, soil octagons, finite/nondegenerate geometry, closed supports, UV cardinality and support graphs. `CONTRACT_CHECK_REPORT.json` records the latest pure result.
4. `check_planned_contacts.py` independently tests 1,908 real planned child/parent triangle contacts, positive support volumes, non-flat shaped leaves, and all 120 audited screen probes. Its passing report does not replace evaluated-source QA.
5. `test_predicates.py` covers inside-vs-AABB, finite ray segment limits, off-plane surfaces, real octagonal chamfers and the low/upper reservation boundary.
6. `build_sources.py` only authors editable .blend files into fresh descendants of its own installed package, whether the approved package is still in scratch or installed in the new catalogue sibling. It uses fresh-path guards, preserves surviving candidates, appends materials only from different pinned originals, links objects before updating/evaluating, and never exports or renders. Its receipt records that exact write scope and does not claim zero catalogue writes when installed there. It makes no preference setting change.
7. `verify_sources.py` independently reopens each saved source, evaluates actual mesh transforms/triangles/UVs, checks exact expected geometry, non-flat leaves and clean boundaries, closed positive-volume supports, actual geometry at every attachment, soil contact vertices against the actual retained export triangles, marker transforms, and actual original packed material bytes. Vertex comparisons retain the planned JSON doubles and record true maximum deviation per part and per source. Closed volumes use float64 arithmetic after a per-part local anchor shift and are recorded per support. For the wet whorls it appends the original basal crown, proves positive-volume overlap, reads the actual pot export, and establishes leaf/rim clearance. It repeats the 120 screen probes from evaluated triangle coordinates. It never loads a .blend as a library into itself, saves over sources, exports or renders.

## Coordinated source-slot commands (not executed)

Run from this directory with the parent's verified Blender executable:

```
blender -b -t 2 --python-exit-code 1 --python build_sources.py -- --output candidate_v001
blender -b -t 2 --python-exit-code 1 --python verify_sources.py -- --candidate candidate_v001
```

No concurrent Blender/render/Godot job should be launched by this package. A focused diagnostic can use `--only` with an exact placement name and a fresh candidate directory. Do not overwrite a failed candidate; retain its receipt and choose a new versioned directory after a reviewed repair.

After the independent verifier passes, the parent independently retains the candidate .blend files, complete contract, scripts, input pins and QA receipt with verified recovered hashes. Export must wait for both that retention and parent review. No export script or automatic adoption hook is included here. Source-context and final engine visual gates in `VISUAL_REVIEW_RECIPE.md` remain required.

## Limits

The 50 mm modeled soil cap is not evidence of horticultural soil depth, load, irrigation or species suitability. Foliage stays non-colliding; this package does not add a blocking canopy hull. Exact mesh reservation and source contact success does not certify actor/maintenance circulation, a readable planted composition, engine import, target-hardware performance, or room completion.
