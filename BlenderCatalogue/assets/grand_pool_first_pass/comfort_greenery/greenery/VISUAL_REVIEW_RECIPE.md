# Visual review recipe: fuller plants must read in the room

Do not treat a geometric pass, a high leaf count, or a close-up beauty image as acceptance. No review renders have been made by this package.

## References actually inspected for this candidate

- Game `artifacts/grand_pool_market_bays_clear_world_capture.png`: the black soil tray overwhelms three thin, isolated plants; broad connected low/middle mass is missing.
- Game `artifacts/grand_pool_long_view_clear_world_capture.png`: tiny wet pots almost disappear, so they cannot honestly carry the long-pool composition. The large market planting pockets must establish the main botanical rhythm.
- Game `docs/references/cruise_atrium_20261006/retro_atrium_quality_benchmark.png`: filled bed surfaces, connected middle foliage and unequal crowns soften architecture. Reference building geometry and photo pixels are not copied.
- Catalogue `references/aquatic/image(20261001-035517).png`: strong low/middle/high silhouettes, substantial green masses and restrained flower accents frame water and circulation.
- Catalogue `assets/botanical_understory/qa/understory_raw.png` and `assets/botanical_cluster/qa/AST-BOT-007_source_640.png`: inspect the real retained faceted, cupped/fan material and silhouette vocabulary. These assets are useful lineage, but individually sparse.

## Stage A: source review after evaluated QA and retention

Assemble copies in a new review-only .blend. Use the actual retained architecture/planter, the unchanged original plants and the three proposed derivatives at their declared positions. Do not replace originals with proxy boxes. A world glTF position `[X,Y,Z]` maps to Blender `[X,-Z,Y]`; each derivative's local source stays identity-scaled.

Review all six beds, with special attention to the bed at Z -446.7. Show:

1. A normal room-side perspective of each complete planter, three layers and retained plants together. Its silhouette must read as one connected living bed with unequal high points, not nine identical rosettes or a rectangular hedge.
2. The first bench's left/right seated views, using exact world eyes X -50.948 / -49.852, Y 53.50, 53.68 and 53.90, Z -448.79. Include the parent's final full display housing and mounting pieces. Aim each view at the complete final image rectangle; compare its four corners and centre. Low west cover must remain generous without entering the image view; taller east foliage must look naturally composed.
3. A three-quarter close view of the wet pot, original rosette plus additive whorl, with the actual pot rim and original soil top. Inspect the crown join and leaf/flower attachment at useful scale. Do not showcase only the additive whorl floating alone.
4. A neutral diagnostic view with wire overlay solely for the contact/pleat/UV checks; keep it separate from the normal material image. Check curled surfaces from both sides, no black reversed faces, no z-fighting petals, no collapsed fan pleats, no floating roots or thin unsupported stems.

Use pinned original materials without recoloring or emission. A source-preview light rig belongs only to the review scene and must be documented; it is never proof of the installed lighting, never saved into derivative sources, and never adopted as added game fixtures. Do not alter shared render or palette settings to improve the result.

## Stage B: matched actual engine comparison after separate export/import gates

Retain before/after pixels with identical camera, viewport, exposure and existing/planned light state. Use the existing `grand_pool_section` presentation route; the following are current actor spawn parameters read from `scripts/presentation.gd`, not invented absolute camera eyes:

- Market bays: actor position [-45.9,52.6,-439], yaw pi/2, pitch .04; retain the camera's existing offset and projection.
- Long pool: actor position [-20.5,46.3,-405], yaw 0, pitch .03.
- Market overlook: actor position [-45.9,52.6,-432], yaw -pi/2, pitch -.18.

Inspect both the ordinary presentation and effects-off world capture at native 640x360 as well as the uncropped larger diagnostic image. Keep exact filename, image hash, camera state and capture mode with each result. No sharpened or saturated replacement screenshot is admissible. Any new seated camera must use its stated eye coordinates rather than the standing actor camera offset.

Acceptance observations:

- At 640x360 the trough has contiguous broad green low and middle masses; most formerly black soil is visually softened. Flowers punctuate rather than becoming tall pins. Upper fans remain chunky and recognizable.
- Across all six beds, crown heights and outlines vary. Reject identical clone silhouettes, uniformly flat carpet, fluorescent greens or criss-crossing stems that look physically disconnected.
- The first display remains legible in its entirety from both seats. The low foliage and east crown both look intentional. A ray pass is not a substitute for this image review.
- In the unzoomed long-pool view, the six market beds read as a repeated planted architectural layer. Report honestly if the reference-level long-view rhythm is still weak; five tiny wet whorls are not an excuse to claim it solved.
- Do not conceal important windows, wet/dry glazing, pier shapes, water views or the central void. Leaves may overlap other intentionally composed leaves; they must not disappear into walls or floors.
- Run short ordinary/effects-off pans past a representative ordinary bed, the first screened bench, and a wet pot. Watch for flicker, aliasing and visual repetition. Walk the established approach and maintenance routes with the same actor/collision setup. No moving seats or routes to make plants fit.

## Required record

For every reviewed view, record `PASS`, `FAIL` or `NOT_RUN` for fullness, style, contact appearance, screen visibility, composition and circulation. Add specific observations and actual image paths/hashes. A failed visual condition calls for a new versioned candidate and rerun of affected source/contact/export checks. Never label the room complete while ordinary engine pixels or circulation remain unreviewed.
