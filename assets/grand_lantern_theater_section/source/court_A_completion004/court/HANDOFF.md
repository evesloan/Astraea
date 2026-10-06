# Court A additive fit, revision 4

Status: scratch-only geometry/placement preparation. No Blender, renderer, Godot, source rebuild, Catalogue write, Game edit or export was run. The immutable firstpass003 source still hashes to `dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530`.

## Useful result

The current `COURT_A_GEOMETRY_CONTRACT.json` and `COURT_A_PURE_SCREEN.json` form a coherent additive fit: 69 closed architectural/furnishing pieces, 5,728 nominal triangles, 24 exact retained instances and six informal seat contacts. They propose one standalone same-family AST-CUL-005 court derivative, plus a separately composed review scene. All old objects, plants, front usher stations and 2,200 audience chairs stay fixed.

`COURT_A_PLAN_PREVIEW.png` is a inspected geometric plan diagram, not a source/native visual acceptance image.

## Exact placement and reservations

- Both inward-facing planted sofas have a 2.9 m curved sweep, Z−138.9…−136.0. They were shortened from the provisional 3.4 m to preserve occupied staff reservations at the front. Solid overall X bounds: west −73.61875…−71.96; east −67.04…−65.38125. Seat crown Y69.975; back top Y70.495. Three real seat contacts per side face the opposite occupied sofa, with the new reception as secondary focus.
- Each seat has its own curved 0.82 m-deep standing approach; the nearest approach remains 0.12619 m outside the central reserved spine. The inner spine is 3.1 m wide, X−71.05…−67.95/Z−139.73…−134.55. It is not falsely described as a full-length axis through the existing usher.
- The reserved front cross-aisle is 1.5 m deep, Z−135.90…−134.40. Actual separation between the sofa front and retained counter rear is 2.625 m; retained staff pockets reduce that to 1.65 m before reserving the cross-aisle.
- The cart enters from the existing west aisle at (−77.5,−137.5), turns through two 2 m-radius arcs and proceeds down the inner spine. The 325-pose test uses actual cart compound boxes, a carried-load envelope, actual 0.3 m-radius/1.8 m player dimensions, the trailing operator at local Z+1.62 and a 72.16 mm continuous between-pose guard. No geometry contacts or unsupported wheels/operator disk occur. The guarded sweep clears the two retained rear staff pockets by 0.07000 m and 0.40292 m. Main D11 route via X−45.5/Z−151/X−77.5 is untouched.
- New AST-CUL-002 counter: (−69.5,69.5,−140.3), yaw 0, unit scale. Public/front is world +Z; open staff side and drawer travel are world −Z. Closed rear to basin: 1.425 m. Open drawer handle to basin: 1.181 m. Floor-supported service stance: (−69.25,69.5,−141.4). Public stance: (−69.4,69.5,−139.35); lower-writing stance: (−69.97,69.5,−139.38). All capsule bounding prisms clear.
- Two retained AST-FUR-003 tables: (−72.15,69.5,−139.38) and (−66.85,69.5,−139.38), beyond the sofa ends and outside the spine. Exact proposed programme-stack contacts are in `TABLE_AND_COUNTER_CONTENTS_DRAFT.json`.
- Curved backing: X−73.45…−65.55, frontward arc Z−145.66…−145.16, 0.20 m deep; side tops Y72.64 and central crest Y73.36. Walnut dado, actual fabric recesses and fitted frame are NEW geometry in front of the existing glass. Nothing is cut out of old walls, floors or screens.
- Side ceiling undersides Y72.85 give 3.35 m headroom. Six flush brackets bear on the measured inward faces of the six existing piers. Their underside Y72.62 gives 3.12 m. The central open ceiling is at least 4.1 m wide. Old portal top Y74.15 and D12 underside Y77.55 are preserved.
- Grounded sofa plinths approach the existing middle pier feet to 16.42 mm; that fitted seam is not a pedestrian or maintenance passage. No old-solid AABB penetration candidates were found. The 5 mm textile rug is cosmetic/noncolliding, has fitted support/basin/pier holes and earns no walking-floor credit.

## Planting and real materials

All 21 added retained plants have exact unit scale, actual transformed basal and foliage vertices screened, zero foliage outside their soil projections, 3 mm nominal root embed and adequate soil depth. Root-to-root screening covers 42 collars including the 18 preserved roots/collars and three optional fuller roots: 708 relevant pairs, minimum new-to-any actual root-edge clearance 14.32 mm. This avoids the earlier overlapping rear flower origins; earlier drafts remain preserved for diagnosis.

`FULLER_REAR_MASS_CANDIDATE.json` adds three connected middle crowns and 36 whole shaped broad blades, only 2,922 triangles. All emitted vertices fit the actual retained 4.5×1.5 m rounded soil. Roots are at X−70.9/−69.5/−68.1, Y70.1470015, Z−143.08/−143.10/−143.06; 0.5 m soil depth, 3 mm embed. Maximum crown height is 1.73416 m above soil. It uses the pool's independently checked geometric method, never its unretained source assets or route acceptance. Court-specific source build/reopen/visual/retention remain pending. Old emergent BOT-007 fans and all old low plants remain.

Exact retained textures/material roles are pinned in the contract: warm_walnut [0.65,1.3] m/tile; teal/clay/oatmeal weave [0.8,0.8]; champagne_metal [0.6,0.6]; warm_stone/ivory_enamel [1,1]; soil [0.5,0.5]. Each new face has explicit metre-density UV loops, with walnut grain direction recorded. Leaves retain shaped across-blade/root-to-tip UVs. Source adapter appends retained graphs and packed images rather than synthesizing lookalike materials.

## Next short build/look cycle

1. Parent coordinates the source slot after the static checkpoint. Finish the original SunCorp programme image and three small programme stacks; their exact mounts/material requirements are recorded. The graphic is the genuine remaining art dependency, not a blank placeholder to be accepted.
2. Use `build_court_A_source_DRAFT.py` to create only the standalone court in a new scratch source path. It is syntax-checked and inspection-tested, not Blender-tested. It requires an explicit parent source-job gate and fails before Blender work if artwork/checkpoint/slot evidence is absent. Its optional fuller mass remains separately gated.
3. Independently reopen the new source, verify all graph/packed-image/UV hashes, closed architecture, leaf topology, real fixture-bearing faces and botanical joints. Then use `compose_court_A_review_DRAFT.py` to append just its collection to a new copy of the immutable theater for same-camera and seated/service reviews. Preserve old light identities, exposure and the 8-shadow/32-candidate policy. No new lights are part of this contract.
4. Only after the Court A source is independently retained and actual pixels support the composition, export the standalone new asset and coordinate an additive runtime integration. No rebuild/export of the old theater or audience-chair prototypes is required.

Pure screening is not physics, acoustics, load certification, six-species fit or visual acceptance. Those gates are not silently waived.
