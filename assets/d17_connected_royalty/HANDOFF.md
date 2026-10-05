# Connected aft D17 source increment

5 October 2026. Editable architecture and bounded source/export QA. This is the first connected construction increment in the sixteen-unit D17 house within the complete eighteen-deck liner. It is not a completed Royalty suite, new accommodation, separate service network, finished private upper, whole-ship art approval or runtime acceptance.

## Integrate these two exports only

- `exports/AST-RES-006.glb`, authored zero-origin world coordinates. Instantiate at Godot `(0,0,0)` with identity scale/rotation. Its `.blend` contains separately editable parts and four hidden-render wire floor previews. **None of those four previews is exported.** The established floor compiler is the only visible/physical slab owner.
- `exports/AST-COM-003_aft_only.glb`, a variant of AST-COM-003. Use the existing commons placement `(63,84,0)`, unchanged identity and controller family. Replace the current runtime COM003 representation in this increment; do not instance a second copy. Its aft portal is clear X78.5..81.5 / Y102..104.82 at Z13.2. The fore wall and wainscot have been restored exactly from the verified closed source, and the three fore split additions removed. All586 other held objects are identical. The held two-opening source/export remains untouched.

The old AST-RES-005 source/export is preserved byte-for-byte. Do not instance its entire212-part frame. AST-RES-006 contains only eight exact retained components: footings0/1/2; Fore/Aft/WestFore piers; RoyaltyTransfer and RoyaltyTransverseTransfer. No X116 frame, new full-height bracing, or X84/Z24 support was added. The reused objects retain their original source IDs and properties; they are aliases of existing components, not eight new assets.

## Floor and route contract

`source/connected_contract.json` is the machine-readable integration interface. `floor_regions` supplies stable construction IDs, desired XZ boundaries, no holes, Y102 and thickness0.24. The four disjoint footprints total605.2m² and their authored guard perimeter has the same area. Union/subtract them through the existing compiler. Root's dry-run found no retained-floor/void overlap; it selected priority−1 to protect existing owners. This source handoff does not claim that the live compiler or old ownership has changed.

The existing floor reaches Z14. The new approach starts exactly there; the portal atZ13.2 remains on the old floor. The central Z−20..20 view band gains only the3m narrow approach. BeyondZ20, the plan widens into a faceted landing reaching roughly7m depth, with a pause off the turn. A3m lane leads to an arrival bay entirely inside790 at X94..99/Z29..35.5. The actual private threshold is at X97, clear Z30.9..33.9 / Y102..104.82. Its side returns, lowered canopy and offset privacy screen create a recessed arrival before the broader view-led platform.

This first threshold is safely open. There is no moving door or door controller to wire now. The complete AST-DOR-002_wide fitting is reserved at `(97,102,32.4)`, enclosure Z29.82..34.98, with unchanged1.18m leaves/1.24m travel. It must be explicitly fitted and collision-tested before claiming a working door. The lane is never its pocket or parking bay.

Initial cart-centre guide points, not validated physics: `(80,12) → (80,21.5) → (82,25) → (88,25) → (92,25.9) → (92.4,30) → (95,32.4) → (101,33) → (107,36) → (113,40)`, all at floorY102. Receiving area X98..103/Z30.5..35.5 supports fitting the operator/cart release, regrip and turn. Root owns the actual position/heading sweep and force-tethered four-bottle round trip, including backing recovery, return to the same commons lift and ordinary2m/s input smoke.

## Guard, roof, fixture and contact interfaces

- `guards` lists every source-matching continuous exposed edge. Base Y102.025..102.35, glass102.35..103.01, cap103.01..103.09, matching the existing family. Source fascias meet the slab soffit101.76; thin edge trim follows the established boundary-centred family. No rail crosses the existing floor seam or internal union joins.
- There is a physical end guard across X91..94 atZ35.5 for the unbuilt onward luxury lane. The standard branch is closed by the existing west court guard until a supported branch is built. Do not merely add signage and leave an opening into void.
- `fixtures` gives nine world-space source light markers corresponding to visible physical housings/lenses. Use existing local-light behavior/material families. The export also has ten route/reservation markers; these are not lights or collision.
- Ordinary lower roof height stays≤106.30, below the106.5 limit. The narrow approach has a rising soffit; the court, recessed private bay, side bay and outboard view reveal have different overhead depths. The broad outward profile is a platform/view-frame decision, not an accepted external celestial aperture. The real ship hull and in-ship sightline still control what is visible.
- The actual closed-mesh intersection graph is in `qa/source_contact_graph.json`. Roof roots contact the retained top transfers atY101.76. Narrow approach roof edges contact the unchanged `HC_PerimeterTransfer_106.26_1` at `(78.42,106.02,12)` and `(81.58,106.02,12)`. The connected roof/perimeter system and short hangers stay above the D16 slab soffit over590/614. No dropped west transfer or shaft pit consumes those lower-home volumes.
- Contacts are game-construction geometric joints. They do not introduce a real-world engineering certification gate. Existing retained-seat contact evidence is reused; no further hull-compression diagnostics or hull edits were performed.

## Reservations and identity

All16 source indices and null historical stable IDs remain in `units_preserved`. Correct standards are five fore `[868,844,820,796,856]` and four aft `[874,850,826,802]`. House composition remains five Deluxe, one Premium, one Royalty and nine standards. There is no new unit, berth or completed capacity claim.

790 lower floor remains within X94..118/Z29..51; the effective814 replacement allocation is explicitly X94..118/Z51..61, superseding its historical overlap. The luxury lane X91..94 remains continuable aft; the standard branch X76..79 is reserved. Private stair X94.5..99/Z40..49.5, lift/landing X99.5..104/Z43..49.5, and screened care/service X94.5..98.5/Z36..40 are distinct reservations inside790. The floor stays continuous with no holes. Same-unit private upper106.5 and roof≤112 are reserved, not built and not prerequisites to accepting a safe first lower floor.

## Portal side-gap correction

After retained freeze afe3102, eight matching fascia/base/glass/cap source parts close both0.35m side gaps from jamb endsZ13.65 to apron guard startsZ14, atX78.5 and81.5. The actual portal planeZ13.2 and floor polygons are untouched. All prior source objects and the COM variant source/export bytes remain unchanged. `qa/portal_return_verification.json` checks120 actual side rays through the four bands, positive source joints at both ends, and exact baseline preservation. Root still owns the actual small-product escape regression.

## Evidence and stopping point

`qa/source_export_verification.json` verifies the exact oriented source/GLB triangles, UVs, material names, embedded texture bytes, marker transforms, closed positive-volume meshes, preserved original files/COM objects/reused source components, all16 units, and protected D16 height. `qa/dimensioned_plan_section.png` shows the source plan and reservation section. `qa/source_cutaway_review.png` deliberately hides ceiling sheets and the retained tall support subset to inspect the local authored plan; it is labelled source-only here. `qa/source_court_threshold_review.png` shows the actual roof/threshold at normal source camera height. Neither image is an in-ship runtime result.

Actual reference pixels reopened: guest corridor8077, nested view8079, premium broad view, intimate court-facing edge and botanical atrium. Their useful depth, widening turn, private spatial hierarchy and coherent profile informed original geometry. No reference asset was copied.

Root owns import, runtime/compiler integration, original-owner and lower-home regressions, lift/stair/controller tests, actual walking/cart trips, normal/effects-off and full-ship context views, commits and backup verification. Source work stops here after the matched QA freeze; there is no engine process or import from this source lane.

## Restart-safe recipe

From the catalogue checkout, run Blender headless with `source/build_connected_royalty.py`, then `qa/verify_connected_source.py` and `qa/verify_portal_returns.py`. The builder verifies retained dependency hashes before touching this new family and regenerates only this family's source/export/contract. `source/verified_closed_COM003.blend` is the hash-verified retained pre-portal provenance used solely for the two exact fore-wall restorations. Optional `qa/render_source_review.py` and `qa/draw_contract_plan_section.py` regenerate the local source review. Regeneration changes `.blend` hashes; rerun QA and then `python qa/finalize_delivery.py` after any optional review images to refresh the catalogue registration and delivery hashes before copying to runtime. No restart requires rebuilding the old frame or running Godot from this lane.
