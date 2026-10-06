# East gallery core: references and authored decisions

6 October 2026. Actual aquatic and Cunard image pixels were reopened before shape authoring. The governing architecture brief, current-phase direction, coordinate contract and architectural profile QA were reread. Their exact hashes remain in the parent DESIGN_INPUT_PINS.json and are rechecked by plan_core.py.

- Aquatic diorama: use the cream layered edges, deeper warm destinations and substantial full greenery. The response is one 9 × 3 m room-shaped bay, with curved full-height returns, a concave clay back and a broad two-level canopy whose front is lower than its warm back. No reference decks, pools, bridges, windows or new floor are copied.
- Cunard Queen Elizabeth: use the useful vertical arrival and strong material-lined threshold. The lift gets one quiet uninterrupted convex two-level skin, with an aft directional mounting field pointing toward its real east entrance. The fore sun remains the main pool focal composition. There is no entrance-shaped opening on the opaque west shaft face.
- Governing master: the allocation is a free-volume limit, not a box-room instruction. Plan and section are both authored. The canopy varies from 56.03 m at its ends to 57.55 m at the rear centre; its front forms a different, lower curve. The warm rear and pale front are structural-scale bodies with a real stepped junction, not a collection of thin mouldings.
- Actual use: the 2.72 m continuous bench faces the opposite market and tall volume. Fore and centre positions have clear planned rays to a low, housed side display. The aft position is primarily market-facing. No seated water view is claimed: the retained gallery floor blocks it.
- Plants: two unscaled full BOT-002 crowns and two unscaled BOT-003 basal masses sit on real finite soil. The source-selected origins are X−9.10, Y53.02, Z−452.20/−446.80. Rearward positioning permits the display at image origin (−10.38,54.20,−450.99) with normal (+0.62,0,+0.78460), rather than forcing it overhead. Exact retained meshes and image-corner rays remain the integration owner's gate.
- Use and access: the table sits to the aft side. The principal standing approach/return runs along Z−449.8. A conservative cart stop remains on the original apron; no tight cart manoeuvre through the furniture is claimed. The full 3.2 m apron and 3.4 m dry loop remain clear.
- Materials: the build appends only original retained material datablocks from AST-AQU-016 and AST-AQU-001. It retains their packed image bytes and graphs, uses metre-scaled UVs, follows the bench tangent for walnut grain, and creates no universal recolour or reconstructed material.

## Source-only scope

29 independently editable closed core meshes: 14 architecture/receiver/hanger bodies, four bodies for one bench, three for one table, four for two soilbeds, and two physical light cups with two seated opal lenses. The pending four plants, housed display and two signs bring the proposed programme to 11 entities. Architecture and fixtures are counted separately. The opal lenses reuse the unchanged GardenOpalLens material from the actual retained AST-AQU-016 source. Five non-rendering source markers document three seated eyes and two light reserves; no native light settings are guessed.

The plan and review use Godot XYZ metres. The build explicitly maps (x,y,z) to Blender (x,−z,y), Z-up metres. Saved source parts have identity object transforms. No new unique design ID, production write, export or renderer change is made.

## Geometry review

CORE_REVIEW.json is the controlling core-only planned-geometry result. It checks actual triangle contacts and intersections, true support paths, exact compiler-floor bearing, finite closed geometry, approved reservations, protected routes, apron occupancy, original view and fixture rays, the new approach/return/cart stop and new seated rays. The first failed diagnostic is retained as CORE_REVIEW_initial_diagnostic.json; its planter/bench termination and fixture contact issues were corrected geometrically.

This is not a saved-source acceptance or a combined programme gate. Actual plant/display/sign integration, source reopen, all image-corner rays, early composed pixels, native support/collision, and lighting selection remain later checks.

## Prepared bounded commands; not run

Core source build, no rendering/export, fixed two threads:

    /usr/bin/blender --background --factory-startup --threads 2 --python /workspace/scratch/375c2e438292/pool-opposite-gallery-proposal001/source_blockin001/build_core.py

Fresh-process read-only source reopen:

    /usr/bin/blender --background --factory-startup --threads 2 --python /workspace/scratch/375c2e438292/pool-opposite-gallery-proposal001/source_blockin001/reopen_core.py

The first command refuses any existing build001 directory. Its output is one new scratch .blend plus an evaluated geometry/material receipt. The second writes only new QA JSON. The parent controls the build slot and integration timing. No Blender, Godot, rendering or export was launched while preparing this package.
