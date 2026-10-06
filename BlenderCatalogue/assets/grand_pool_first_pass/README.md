# Grand Pool / Orchard Market first-pass essentials

6 October 2026. NEW package only. This is an additive planning/source-generator delivery, **not completed source geometry, imported content or a completed first-pass scene**. No Blender, Godot, import, render, live edits, original source edits, registry, commit or backup operations were run. All eleven retained source/export pairs are pinned by actual SHA-256 in the generated contract. No external luxury/garden ZIP was assumed to exist and no new model library was invented.

## Actual inspected evidence and gap inventory

Read the updated Game `docs/ARCHITECTURAL_DELIVERY_RULES.md`, connected section specification, catalogue source contract and current lighting review. Opened actual cruise lift photographs, owner retro quality benchmark, original aquatic illustration and actual Game long clear pool view and market-bay world view. The pool capture contains working architectural framing and textured surfaces but a bare long terrace, empty social edges, little botanical occupancy and flat visible lighting. The market capture contains an orange recess and empty built-in planter/seat surfaces; it lacks a purposeful display and inhabitable bay arrangement. These captures are unfinished construction, not visual acceptance.

Implement the evidence's cream/stone frame, darker timber hospitality contrast, warm metal, planted recessed edges, supported light sources and purposeful seating composition through the existing restrained low-poly/CRT pipeline. Do not copy the benchmark crowds, crystal complexity, shop names, extra storeys, celestial roof opening or exterior views. Preserve the 50x18m lane, current 18-deck map, D07/D10 neighbours, stable programme IDs and established stairs/doors/lifts/cart routes. Illustrated spa islands, slides and swimming/retail/NPC operation are outside this package.

## Retained catalogue reuse and current proposal

`source/placement_contract.json` contains 51 world-metre placements:
- Seven AST-AQU-001 sculpted drained loungers and four AST-AQU-002 personal-item tables create spaced wet-side rest stations
- Existing AST-AQU-007 clean dry-towel niche and AST-AQU-008 separated used-return unit give the arrival/rest edge a purpose. Stock already integrated in the dry niche is reused; no new towel gameplay is claimed
- Six existing market soil pockets receive six AST-BOT-002 understory plants plus twelve AST-BOT-003 low rosettes. Their complete foliage envelopes fit the pocket bounds, with separated plants
- Five AST-BOT-012 contained wet-edge pots receive five AST-BOT-003 rosettes at the actual physical soil top of +0.200m. Pot generator source establishes this datum; the .198m empty is slightly below the physical soil top, so it is not used blindly
- Three existing AST-RTL-001 recessed display assemblies and three AST-RTL-004 static small-goods cases fill the existing market programme, without new business identities. Case placement uses the retained manifest's actual `main_display_left_patch` at +.95m, not a guessed shelf height
- Three AST-FUR-001 social pause benches have front approaches outside the market clear loop; one level wet-end bench supplies non-reclining rest

Original materials/textures remain unchanged: ivory/enamel and warm stone frames, warm walnut/metal hospitality accents, existing aquatic/botanical/retail material roles. Inspect exposure/texture scale in the actual game before accepting; no artificial texture or palette replacement is proposed. The source generator appends independently editable retained Blender mesh/marker objects with their original material/texture roles, not copies of generic boxes. It preserves each source object's frozen world matrix before changing parents.

## Bounded geometry planning checks

`source/plan_assembly.py` reads actual GLB POSITION vertex buffers and complete node transforms, rather than trusting title dimensions. Its read-only source inputs are the pinned catalogue exports plus the frozen connected section's source-part geometry and triangulated compiler floors. It writes only this NEW package.

`qa/plan_envelope_report.json` currently has zero issues: conservative 3D AABB checks against every exported existing source-part envelope and other planned assets (except explicitly declared plant/display support owners), protected wet-apron and market loop/bypass rectangles, plus <=.05m footprint samples across each declared floor's actual triangle set. No floor polygon is copied into the assembly. Actual full item envelopes do not overlap existing piers, guards, ramp, local-link voids, door casettes or existing fixtures. The package is deliberately confined to the west hospitality edge and soil pockets; no item enters an existing staff street, shaft, stair/lift pit, eastern arrival/ramp or protected neighbouring volume.

This conservative envelope pass establishes only a bounded planning candidate. Supported child item AABBs necessarily overlap the whole parent display/pot AABB; their final triangle contacts must be checked independently. Dense floor samples are planning evidence, not actual capsule physics. Proper compound static contacts, towel extraction/retrieval envelopes, source contact preservation, parent route poses and operational loaded-cart regressions remain mandatory.

## Source-backed lighting, signage and remaining first-pass gates

The contract carries all 25 existing exact section fixture markers and paired physical housing/lens names. Reuse current runtime profile ranges/energies and culling policy recorded in Game `GRAND_POOL_LIGHTING_REVIEW.json`: vault range22/energy1.1, terrace14/.85, market11/.75, staff6/.8. Do not create floating fill lights or assume 45 simultaneous shadowed lights. The long capture shows why these settings remain a partial lighting improvement. Review source-to-receiver rays, foreground exposure, warm versus neutral hierarchy and orange-bay readability after furnishings. The parent owns any runtime adjustment; no renderer/engine switch is proposed.

Wayfinding is still a mandatory first-pass gap: readable existing-programme “Grand Pool”, “Orchard Market”, “Towels”, “Used towels” and step-free route directions at actual arrivals, coordinated with existing doors/route markers. No new business or unsafe depth/safety label is authorized. There is no verified retained sign-board source in this scoped inventory. A bounded sign derivative needs parent identity/placement review before authoring; this package does not claim invisible text markers are finished signage. Similarly, display cases are static scenic content, not complete stock/retail operation. No fake crowds or NPC acceptance.

## Parent-scheduled next steps

1. Review placement contract, source-backed support contacts and retrieval/extraction/seat-approach envelopes; resolve signage derivative allocation
2. Schedule `source/build_editable_assembly.py` in Blender; do not run concurrently with parent jobs. It fails closed on changed pinned sources, unresolved plan issues or an already surviving assembly source
3. Verify new source-part/world transforms and material/packed texture integrity; independently retain source before export/adoption. Generator only saves the new editable .blend, deliberately withholding export pending review
4. Allocate export/compound contacts and Game adoption without changing established floors/routes/voids or controllers
5. Repeat actual capsule/closed-door market loop, local lift, loaded four-product cart including reverse/regrip, preserved108 existing-project checks and normal-height/effects-off in-game review. First-pass completeness includes actual materials/textures, source-backed lighting, furnishing, planting, essential stock/storage and wayfinding. Later polish refines this baseline

No new catalogue identity was assigned. The programme IDs and retained sources stay authoritative. Current source hashes and source-only findings do not imply live runtime or visual acceptance.
