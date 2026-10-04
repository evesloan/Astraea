# Arrivals and fusion-gallery integration

## Governing direction
The user approved a curated technological exhibit above the arrival lobby on 4 October 2026, with service catwalks and maintenance hidden from guests. Cunard Queen Elizabeth informs the ceremonial stair, layered overlooking galleries and focal wall; it is not a source of copied art. Master v0.3 chapters 5, 21 and 32 govern spatial hierarchy, materials, local light and normal-player review.

Both original programme envelopes remain at X -54 to -8, Z -466 to -398. D01 is Y0, D02 Y6, and the opaque protected D03 slab has underside Y11.76. No engineering relocation, crew-room deletion or berth change has been performed. The 68m relocation remains only a conditional user-approved fallback.

## Current construction
- Editable AST-ARR-002 architecture and AST-ENG-007 contained machinery are integrated into the main ship as work in progress
- A wide first stair rises to an intermediate landing, with two lateral flights reaching separate upper visitor galleries
- The existing two-stop physical lift implementation is parameterized for this district; the original commons IDs and configuration remain its defaults
- Upper public floor, hidden staff floor, exhibit volume and gross programme allocations are recorded separately
- Opaque service corridors, end-access bays and the D03 boundary protect maintenance and crew areas from public views
- The main public entrance remains X-8, Z-432, with a supported connector to the existing axial route

## Visual-review correction
The first in-engine captures failed to make the machinery visible enough from the normal entrance. Broad surfaces also felt empty and insufficiently composed. The current revision brings the two glazed exhibits over the arrival court, narrows the visitor galleries around them and moves the upper stair flights laterally to preserve headroom. Transfer shoulders moved up to the case-bearing level after an actual capsule traversal detected a collision. This is a real failed attempt and correction, not a claim of finished art.

Reception, purposeful waiting groups, complete wayfinding, richer vertical illumination, NPC use and final architectural acceptance remain outstanding. Service-access screening tests are geometric visibility checks, not reactor engineering or radiation certification. Cloud captures do not establish target-GPU performance.

## Verification
Current focused results and full regression status must be taken from their latest logs. Earlier checks are invalidated where geometry changes. Run tools/validate.py and inspect player-height entry, court, overhead glance and upper-exhibit captures before committing the integrated phase as checked.

The 09:55 UTC checkpoint passed all29 Godot groups, including actual loaded arrivals-lift travel. The revised overhead composition is visible in ordinary court captures. Focal-wall light remains insufficient; the next refinement addresses its real source/occlusion relationship alongside reception and waiting areas.

## Hospitality refinement after the first integrated checkpoint
Independent review of the real in-game views found that the exhibit dominated the hospitality composition, the upper galleries were hard to read, and the reception desk was isolated against a blank backing. The subsequent pass:
- Gives existing gallery edges a deeper cream profile and timber reveal, without changing floors or guard lines
- Moves the previously axial hanging fixture to a public landing, with a corresponding fixture at the opposite landing
- Replaces the uniformly luminous machinery sleeve with a darker contained instrument and selective glowing bands
- Adds an original three-height crescent reception desk, a fitted fan-shaped wall/ceiling enclosure, three mounted task lights and two purposefully grouped waiting areas
- Preserves six checked capsule approach positions at the reception stations; terminals and staffing remain inactive

A lighting defect was also identified: an emitter aimed away from the player could be rejected even while its illuminated wall was visible. The shared eight-source budget now accepts one explicitly authored receiver only if it is inside the real spotlight cone/range, reached without opaque obstruction, and itself visible from the player. A test rejects a receiver hidden behind the focal wall. This does not create an extra light budget or turn shadowed fixtures into wall-leaking unshadowed lamps.

The latest captures still show sparse supporting surfaces and an overly bright focal patch. Grand hospitality composition and final art are not approved. Screening checks sample25 sightlines; they are not exhaustive moving-view coverage. Component knee-space verification is a measured local empty prism, not universal species-accessibility certification.

## Stair-court spacing revision
The user identified the overhead cases as too close to the stair. Normal court views confirmed the compression: the original7m-deep cases left a2m nominal slot (about1.77m between projecting frames) above a6m stair flaring to6.9m. The reviewed first revision narrows each case to4.6m around the unchanged original machinery, moving machine axes1.2m outward. The nominal opening is now6.8m, approximately6.57m between frames. Galleries, hidden service links, stair flights, deck elevations, lift and protected programmes remain unchanged. A more extreme outward relocation was rejected because gallery slabs would hide the machinery from below.

The review also found a0.7m longitudinal mismatch between suspension yokes and architectural crossbeams. Crossbeams now derive from the actual exhibit-axis midpoint, and four ray checks verify bearing contact. Focused import/arrivals validation passes7.3322seconds. The first test attempt failed because exact imported marker names did not preserve punctuation; bounded prefix lookup plus exact local-coordinate assertions corrected that test. Source/export dimensions and UVs pass. Same-camera visual comparison and full regression are still pending for this revision; opening width alone is not grandeur acceptance.

The revised same-camera entry, court and overhead captures were reviewed after graphical batch arrivals-case-widening-001 (73.892seconds). Independent review confirms that the machinery now frames the stair and the relief is legible; the distant entrance still compresses the composition under a low canopy. All34 regression checks passed in89.65seconds fixed60 simulation. Next refinement: improve the entry-to-court height reveal within the existing D02 slab clearance. This is a targeted improvement, not final lobby approval.
