# Grand Pool / Orchard Market first-pass essentials

6 October 2026. Editable source repaired and checked, **not imported content or a completed first-pass scene**. The surviving 51-placement assembly was built before interruption and its first source QA failed. The original failed file and report remain preserved. Source-only Blender repair and checks have now run; no new GLB, Godot import/run/render, live edits, original catalogue-family edits, registry changes, commit or backup operations were performed by this package worker. Parent owns retention and adoption.

## Verified resumption and route correction

The interrupted generator recorded unlinked Blender objects' stale identity `matrix_world` caches. That misplaced translated/rotated beams, cushions, seams, markers and recessed caps. `source/repair_editable_assembly.py` restores the actual evaluated original world transforms rather than hiding errors with tolerances. It checked all 1,742 mesh/marker objects; restored 203 transforms; and compared every evaluated vertex in all 1,633 meshes. Maximum source-world deviation was 0.031 mm. Raw source mesh geometry, UVs and material-role assignments were preserved. All 22 retained source/export hashes still match.

The original placement plan omitted the already-tested X−45.9 wet walking route. Loungers had only 6 cm visual clearance from its centreline, insufficient for the actual 0.3 m-radius player. After source/architecture screening, exactly seven loungers moved 0.5 m west to X−47.5. The actual route stayed unchanged. `source/plan_assembly.py` now protects its 0.32 m-radius envelope as well as all original circulation bands.

Current authoritative package source: `source/grand_pool_first_pass_editable_corrected.blend`, SHA-256 `815effcaa856b8c776934ddddab2a86f50b892586f2ccfc7823b596ea2be3434`. `qa/editable_source_report.json` records zero evaluated bounds/support/image/hash issues for all 51 placements and 237 packed images. `qa/source_approach_report.json` passes 902 conservative source-envelope/floor samples on 17 approach branches: one supported side of each lounger, both candidate positions on each bench, and towel retrieval/return stances. The used-return extraction and staging reserve is clear of other source envelopes. These source checks are not Godot capsule, occupied-seat, towel-operation or loaded-cart acceptance.

Preserved earlier evidence:
- `source/grand_pool_first_pass_editable.blend`: failed interrupted assembly, unchanged SHA-256 `e7e38474d92294ad7a007deb0434b034736ad9117c245aa6e7fdf365b57e8e67`
- `source/grand_pool_first_pass_transform_repaired_only.blend`: transform-corrected pre-route-revision source, SHA-256 `5c2b0f758ea13709591de16fc0e710c62f3eaf80154b3f5f3f6ca53a84e4b31e`; this is the file state measured in `qa/transform_repair_report.json`
- `qa/rejected_source_report_20261006.json` and original failed verification log: retained without tolerance alteration
- `qa/lounger_route_revision.json`: exact seven-placement-only revision and its source hashes

Use existing retained GLBs as runtime instances; do not export the entire editable assembly into a redundant combined asset. The corrected Blender scene preserves independent authorship and source verification. Seven used runtime files already present in Game hash-match the pinned catalogue exports. AST-AQU-007, AST-AQU-008 and AST-RTL-004 require their exact retained GLBs copied under their distinct existing identities; unused AST-RTL-002 does not need adoption.

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

Original materials/textures remain unchanged: ivory/enamel and warm stone frames, warm walnut/metal hospitality accents, existing aquatic/botanical/retail material roles. Inspect exposure/texture scale in the actual game before accepting; no artificial texture or palette replacement is proposed. The source generator now links and evaluates the complete retained hierarchy before freezing each object's world matrix and changing parents. The separately repaired surviving source preserves independently editable original mesh/marker objects and material/texture roles.

## Bounded geometry planning checks

`source/plan_assembly.py` reads actual GLB POSITION vertex buffers and complete node transforms, rather than trusting title dimensions. Its read-only source inputs are the pinned catalogue exports plus the frozen connected section's source-part geometry and triangulated compiler floors. It writes only this NEW package.

`qa/plan_envelope_report.json` currently has zero issues: conservative 3D AABB checks against every exported existing source-part envelope and other planned assets (except explicitly declared plant/display support owners), protected wet-apron and market loop/bypass rectangles, plus <=.05m footprint samples across each declared floor's actual triangle set. No floor polygon is copied into the assembly. Actual full item envelopes do not overlap existing piers, guards, ramp, local-link voids, door casettes or existing fixtures. The package is deliberately confined to the west hospitality edge and soil pockets; no item enters an existing staff street, shaft, stair/lift pit, eastern arrival/ramp or protected neighbouring volume.

This conservative envelope pass establishes only a bounded planning candidate. Supported child item AABBs necessarily overlap the whole parent display/pot AABB; their final triangle contacts must be checked independently. Dense floor samples are planning evidence, not actual capsule physics. Proper compound static contacts, towel extraction/retrieval envelopes, source contact preservation, parent route poses and operational loaded-cart regressions remain mandatory.

## Source-backed lighting, signage and remaining first-pass gates

The contract carries all 25 existing exact section fixture markers and paired physical housing/lens names. Reuse current runtime profile ranges/energies and culling policy recorded in Game `GRAND_POOL_LIGHTING_REVIEW.json`: vault range22/energy1.1, terrace14/.85, market11/.75, staff6/.8. Do not create floating fill lights or assume 45 simultaneous shadowed lights. The long capture shows why these settings remain a partial lighting improvement. Review source-to-receiver rays, foreground exposure, warm versus neutral hierarchy and orange-bay readability after furnishings. The parent owns any runtime adjustment; no renderer/engine switch is proposed.

Wayfinding is still a mandatory first-pass gap: readable existing-programme “Grand Pool”, “Orchard Market”, “Towels”, “Used towels” and step-free route directions at actual arrivals, coordinated with existing doors/route markers. No new business or unsafe depth/safety label is authorized. AST-RES-001 contains retained RES_MapFrame/RES_MapBacking parts that are a possible sign derivative; their existing 3.12 by 1.45 m outer frame is not yet a fitted Grand Pool sign. A bounded derivative needs parent identity/placement review before authoring; this package does not claim invisible text markers are finished signage. Similarly, display cases are static scenic content, not complete stock/retail operation. No fake crowds or NPC acceptance.

## Parent-scheduled next steps

1. Independently retain this verified editable-source revision and its failed/earlier evidence; parent owns the scoped commit and single backup publisher
2. Review the additive runtime composition and focused-test drafts. Instance the ten used retained designs with exact hashes; copy only the three missing exports. Use faithful component contacts, not whole-object convex hulls that fill towel or furniture openings. No new compiler floors, controllers or new business identities
3. Integrate through a separate Grand Pool first-pass builder without modifying the existing connected-section builder, lighting budget, retained route tests or presentation script
4. Run import-first focused checks including actual capsule access to the 17 new approach branches, source/collider support, towel reach, closed-door market circuit, local lift and the physical four-product cart with reverse/regrip. Re-run the unchanged retained route/floor suite and matched final aggregate regression
5. Review ordinary-height normal/effects-off views. Furnishings alone do not fix the broad blank gray walls/ceiling, flat visible illumination, untreated high wall fields, unreadable distant warm bays or absent directional signs. These are first-pass essentials, not polish
6. Author the next bounded wall/ceiling/fixture/sign derivative only after parent placement and identity coordination. Inspect and preserve every protected neighbour, physical light housing, doorway, sightline and route

No new catalogue identity is assigned. Programme IDs and retained sources remain authoritative. Static towels and retail cases do not establish operated inventory, swimming, NPC use, species ergonomics, target-GPU performance or final visual acceptance.
