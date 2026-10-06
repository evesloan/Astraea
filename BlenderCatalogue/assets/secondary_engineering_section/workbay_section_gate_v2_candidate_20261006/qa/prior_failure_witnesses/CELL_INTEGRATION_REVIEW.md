# Lowered workbay integration review

Read-only review, 2026-10-06. No Game edits, engine launches, or Godot imports. Reviewed live AGENTS/current application/contracts, the retained final-source proposal, scratch compiler result, and both gate drafts. Findings below apply to GLB SHA256 `887f0f68604091c3600203cba42c1a371aef090c2be1419b3bbc185c99e5a041`; a later corrected derivative requires fresh checks.

## Decision

The floor delta is narrow and independently verified. Runtime adoption is blocked by fixed-source collisions in the moving gate and an under-tread portable-object contact gap. The existing guards require a chained, explicit floor revision; historical proof files and every old258 record should remain unchanged.

## Confirmed source failures

### 1. Outside call-button housing crosses the gate's actual moving glass

Fixed housing bounds: X21.79..21.916, Y6.98..7.22, Z−405.31..−405.15. Actual glass moves in plane X21.868. Its complete leaf/frame contact bounds are X21.84..21.895, Y6.03..8.44, with Z moving from −405.12..−403.88 to −406.34..−405.10.

Opening begins entering the housing at approximately fraction `(405.15−405.12)/1.22 = 0.02459` and full-open remains intersecting. At half-open, world point X21.868/Y7.10/Z−405.23 lies on the actual translated visible glass and inside the fixed housing. This is not an inflated query margin or a roller/track-support contact.

### 2. Stair handrail tips intersect actual closed leaf frame

The un-grown exact leaf closed bounds intersect six fixed handrail triangles. At Y6.936/Z−405.1199, the north handrail starts at X21.89299955 while actual source leaf frame occupies X21.84000015..21.89500046: approximately2.001mm actual penetration. The north rail remains in the moving contact sweep; both upper tips need clearance from the closed rest frame.

The exact un-grown closed/open union intersects22 fixed source triangles:8 in SectionStatic_0_WORKBAY (outside housing),14 in SectionStatic_3_WORKBAY (handrail tips). No guide/roller/track triangle is included. Complete vertices, pose witnesses and source hashes are in CELL_GATE_FIXED_CONTACT_WITNESSES.json. These have been sent to the source author for a narrow, separately versioned correction.

The draft `_sweep_occupied` deliberately considers only CharacterBody3D/RigidBody3D (lines92–94); therefore these fixed collisions would not prevent its animation. Do not fix this by broadly considering all fixed objects in the occupancy query, which would merely jam the gate. Correct the source fit and separately assert that every actual moving-leaf shape clears fixed architecture.

### 3. Thin flight contact permits a portable bottle inside rendered solid treads

Visual tread boxes extend down toY5.31, but their own contacts are excluded. The only flight prism is0.12m deep. AtX22.1 its underside isY5.78, while the lower slab ends atY5.55. There is thus a contact-free internal pocket.

A witness using actual cleaning_bottle.gd dimensions (CylinderShape radius0.057m, height0.25m) lies lengthwise alongZ at center X22.19,Y5.61. Its center can move fromZ−405.45 to−404.70. The entire swept bounding envelope X22.133..22.247/Y5.553..5.667/Z−405.575..−404.575 intersects zero fixed, glass-proxy, flight or moving-leaf triangles. It stays3mm above the compiler lower slab and enters the rendered solid tread. The grounded guard post atX22.1 is avoided, not ignored.

This is a geometric failure witness, not an engine simulation claim. See CELL_UNDER_TREAD_GAP_WITNESS.json. A narrowly source-bound underflight closure/fill, keeping the inclined walking contact and lower-floor ownership intact, is a possible fix for parent/source review. Do not restore all stepped top contacts or modify player.gd as a shortcut.

## Independent floor delta verification

CELL_FLOOR_DELTA_REVIEW.json and review_floor_delta.py record a standard-library triangle clipping/area audit:

- Exactly one existing compiled/layout owner changes: D02_secondary_engineering_floor.
- Its layout changes only `holes`; all other layout keys and all other existing layout records are equal.
- Exactly one owner is added: D02_secondary_engineering_workbay_cell_lower.
- All258 original whole compiled records are exactly equal, including metadata/chunks, not just geometry.
- The previous engineering cap and visitor gap remain exactly equal to the pinned additive proof.
- Upper area decreases3128→3112.66m². The exact X21.9..27.1/Z−406.6..−403.65 rectangle is15.34m².
- All upper triangles are inside the old boundary; zero positive-area overlap with the hole; zero pairwise overlap. Areas tile the original boundary minus the hole.
- Lower triangles tile precisely that rectangle with zero overlap/outside area, topY5.55/thickness0.24/undersideY5.31.
- Only upper compiled triangles, rings, structural_area_m2 and render_chunks change. Standard compiler and design contract bytes are unchanged.

This verifies compiler output mathematics, not that main-scene imported contacts use that output.

## D01 reserve

The current programme ledger and whole-ship section coordination place D01_directory_02 Cold provisions atY0, allocationX8..54/Z−466..−398, directly under the recess. It remains required/architecture-pending; geometry_owner is null. The retained source's reserve prose and floor underside5.31 are consistent with that obligation. Neither the scratch compiler layout nor a separate current structured reservation gives the future D01 author an enforceable local ceiling/keep-clear volume.

Before adoption, add an explicit source-linked architectural reservation (not a duplicate physical floor) for the local footprint up to the undersideY5.31, preserving D01 programme identity and pending status. Future D01 ceiling/structure/equipment may not consume this space without an explicit coordinated revision. Do not claim full5.31m usable room headroom: finishes, services and future D01 fit remain unplanned. Assert no new engineering source/contact extends belowY5.31 in the footprint, and actual bottom-facing lower-slab rays return the compiler owner atY5.31.

## Guard-preservation design

Keep SECONDARY_ENGINEERING_ADDITIVE_PRESERVATION.json SHA256 `ee806149c47846c5d2a2374269615f2c13c681b949cea8f2ceb05ad81856e6cc` and SECONDARY_ENGINEERING_RUNTIME.json SHA256 `bef8d64a2238d96a11907083c1ad68aa3db484f71e504299d0c0613ccd9606da` unchanged.

Add a separately pinned sectional revision proof containing both preimages, the exact pre/post upper whole record, the exact new lower whole record, exact layout pre/post rows, source contract/model hashes, and old/new global hashes. Validation should:

1. Authenticate the old proof/contract and authenticate the new revision proof.
2. Reconstruct/authenticate the old261 roster from258 original records plus the old3 additions, or verify a pinned retained preimage with the original validation routine.
3. Match each old258 whole record directly in the new262 roster.
4. Match cap/visitor gap to original proof unchanged. Match upper owner to the exact approved revised record, and its before record to the old proof.
5. Permit only the one new lower ID and only the upper hole mutation in layout; require exact262 roster/one physical node per owner and no additional exemptions.
6. Return the exact current4 engineering owners to downstream guards while retaining every other old guard assertion.

Do not merely replace old hashes/counts with the new ones or weaken equality to IDs/bounds. The old guard presently checks current file hashes and261 exact count, so it is expected to fail after a correct revision unless this explicit chain is integrated.

Affected strict consumers found: validate_secondary_engineering_access.gd, validate_secondary_engineering_essentials.gd, validate_grand_pool_access.gd, validate_d17_connected_access.gd, validate_aft_crown_platform_structure.gd and validate_upper_horizon_enclosure_structure.gd. Each contains261 and/or3-engineering-owner assertions. Update only the named delta, while retaining all original250/245/258 floors,8 pool owners,4 aft owners, D17 proof, support samples, route checks and hash pins. New lower support samples must not be represented as an exception to old floor checks.

## Focused actual in-engine assertion plan

### A. Import/contact ownership

- Refresh imports under the established validation runner, verify source MD5 against remap/cache and frozen model/contract hashes.
- Instantiate exactly one section derivative at identity, retaining original section/essentials; no dense_bays duplicate.
- Assert exact120 actuator IDs, exactly2 gate targets and one persistent gate ID. Buttons must not increase calibration count.
- Assert one moving AnimatableBody with only its intended CollisionShape and no descendant StaticContact; source leaf parentage/global rest pivot must match markers to1mm. Exact closed/open source bounds and travel must match under final imported transforms.
- Important integration trap: ship.model() calls _static_contacts on every visible mesh. The draft gate does not remove a preattached StaticContact. Classify contacts before using that helper or remove only explicitly named automatic contacts and assert the removals. Visual glass, visual treads, controls, calibration meshes and `none` groups may not silently become static solids. Hidden proxies/flight must gain their required intended shapes.
- Assert exact10 pane proxies, each26mm source-fitted thickness; visible sheet has no duplicate contact. Do not create an enclosure-wide hull.

### B. Floor/topology and reserve

- Run chained262-owner proof and require exactly one physical structural collider per owner, no source preview floors.
- Sample old upper slab outside the hole, near each cut boundary, retained turn square, and upper approach; hitY6 on the original upper owner.
- Within empty lower landing/service-face samples, ray fromY6.1 toY5.4 must first hit new lower owner at5.55, never an invisible upper slab. For stair samples require the exact flight owner instead; for visible machinery require its named supported contact, not an exclusion masking collision.
- Probe lower underside fromY5.30 upward and all four rim side faces. Verify5.31 underside and no new contact below it. Preserve cap-owner underside11.76, visitor gap and every old support test.
- Keep bound ledger/reservation checks for D01 Cold provisions and D03 above.

### C. Original player staircase and loose objects

- Use unchanged player.gd, capsule radius0.3/height1.8, ordinary input3.1m/s; do not pass via teleports between flight endpoints or manually overriding move_and_slide for the claimed route.
- Real upper arrival→outside button→open gate→upper approach→flight→lower landing→south machine face→reverse route; repeat in both directions and near both tread-side edges with adequate capsule clearance.
- Sample actual contact support/foot datum every frame. Flight reference top isY=6−0.5*(X−21.9), slope26.565°; expected floor normalY≈0.894427. Upper/lower stable foot levels6/5.55. Test seams at21.9 and22.8, stopped/restarted midflight, oblique approaches, and no collision through rail/glass.
- Closed gate must stop a normal walking attempt from both sides. Open gate must permit passage without disabling leaf, pane or stair contacts.
- Released upright and sideways actual portable bottles must not enter visible stair solid, fall through seams, or become unrecoverable. Reproduce the gap witness above. Count stable IDs before/after recovery, no duplicate stock.

### D. Gate state and targeting

- Both designated approaches must select the exact Area/target through actor.target_from_view(), within2.5m; actual RMB/E dispatch opens/closes, unfocused E does nothing. Recheck all fractions and both sides; no ray through a pane to a hidden control.
- Source-only approach rays currently clear: outside camera-to-marker1.066722m; inside1.430986m; sphere first entry is26mm before marker. This is supportive geometry only, not a substitute for actual first-hit proof with final imports/all old contacts.
- During every physics animation frame, query every actual leaf shape against fixed bodies (exclude only the moving leaf itself). Require no hit, no saturated result buffer, and assert mesh/shape alignment; repeat opening/closing and a sampled full0..1 pose sweep. Intentional guide/support contacts need an exact individually justified source contract, never a broad fixed-owner exclusion. This catches the present22 triangles.
- Place original player and a real loose rigid product in aperture and pocket: initial activation blocks without changing desired state; mid-motion obstruction arrests before penetration; removing it resumes the existing intended state. Test opening and closing, repeated press/echo, reversal and motion endpoints.
- Pause using the existing directory/tree-pause path (presentation.gd), not Escape alone; tree pause must freeze leaf, then resume without jump. Escape only disables gameplay controls in player.gd and is not the same lifecycle.
- With held bottle/cart handle, focused E must release that object first and must not toggle gate in the same event. Then target the gate normally. Retain all old service, entry and privacy door behavior/dimensions.

### E. Upper cart and portable workflow

- Park real cart with four retained products on the upper route; validate its actual wheel/operator support and loaded envelope, and an unobstructed remaining staff approach. Parking inside the turn is temporary operational occupancy, not static free-turn proof.
- Release handle, pick an existing actual portable item, carry through gate/down stair to machine face, return and replace; use held-object priority above. Test a drop near stair/threshold and ordinary recovery. No cart descent or cleaning-task claim.

### F. Lighting/regression/visual

- Keep unchanged8 active/32 candidate selector; prove all proposed emitter exits, named intended receivers, visibility selection along both levels, shadows, and no through-wall illumination. Preserve old9 fixture-owner assertions and source pins separately from new sources.
- Run focused old engineering access/essentials, old service/entry/privacy door checks, floor/chained consumers, affected lighting checks, then the parent-scheduled fresh aggregate. A changed source invalidates earlier focused passes.
- Capture original normal eye, outside threshold, lower landing/service face and return views in processed and effects-off modes. Review gate fit, foot/tread discrepancy, glass readability, lighting and cart/tool workflow; no renderer timing as FPS claim.

## Artifacts

- CELL_GATE_FIXED_CONTACT_WITNESSES.json: all22 exact fixed triangle witnesses and actual-frame/glass evidence.
- CELL_UNDER_TREAD_GAP_WITNESS.json: actual-size portable bottle swept-envelope source gap.
- CELL_FLOOR_DELTA_REVIEW.json: independent floor and old258 preservation checks.
- review_floor_delta.py: repeatable read-only mathematical audit.

## Narrow correction verified against actual saved source (2026-10-06 09:04 UTC)

The separately versioned `sectional-proposal/gate-sweep-v2` candidate resolves the gate housing/handrail failures and the under-tread pocket at source/export level. `CELL_CORRECTED_SOURCE_REOPEN_REVIEW.json` passes27 independent checks, including the actual saved-source reopen dump, all47,930 material-tagged triangles, unchanged material definitions, exact five revised/two added source parts, all120 unchanged actuator geometry/material/UVs, continuous exact un-grown exported leaf sweep,201intermediate/end poses,128bottle cross-section side rays and135vertical solid-flight probes. The old frozen source/export remain hash-identical. The flight bottom isY5.55, preserving the compiler slab as soleY5.31 underside owner.

Verified final bytes:
- Source: 0e4d89ac3a76b4f15c67ef41b5179b0a0780dbc1199eea31562b90b92737a6c3
- GLB: 6896d757c5a248d0fcf37a2ae7a197de24566a3fec3f80ce80cdc12186e34368
- Final source contract: b79c0103ef2a8bba9cdea618755fc4d64cc393aaa207e38a0caf9c9e55920ba1
- Actual reopened source dump: c15ccdf2d0496a39eb2886ced43654d78394f1adf8c00ec059b66653a1ad1861

The intentional guide bearing is tangent to the actual leaf bounds. A diagnostic nominal-box test at0.1micrometre tolerance reports six guide triangles because float32 source positions differ from nominal bounds by0.15/0.42micrometres; actual exported bounds and the nominal bounds at1micrometre tolerance both have no interior hits. The failed overly strict nominal diagnostic is retained. This is distinct from the resolved millimetre-scale rail penetration and housing crossing.

Actual runtime1mm-margin shape queries can still report the intentional guide tangency. The focused motion assertion must classify those exact support surfaces/planes and limited tangency depth; it must not ignore the entire merged SectionStatic_3 collider. Godot import, controller/loose-object physics and visual acceptance remain unrun and required.

The draft floor-chain guard also passes19 independent static/byte checks in CELL_DRAFT_GUARD_REVIEW.json. Both frozen pool contracts remain unchanged, with their original261 owner counts and all25combined pins checked through exact successors; essentials9 pins and the pre-existing one-line pool ship.gd addition also match. Old proof pins and old258 whole records remain intact. This is not a Godot parse/execution result.
