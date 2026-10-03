# Retail work components — Batch18

Two original reusable designs; no game or finished shop is recreated.

- **AST-RTL-003**: 1.80 × 0.88 × 1.15 m asymmetric parcel wrapping bench. A raised guest parcel rest is paired with a broad lower staff worktop, rear-open stock shelves, restrained original parcel symbol and inactive abstract staff face. The clear wrapping patch is 0.92 × 0.74 m inside the eased perimeter. It has no moving part, payment system, card reader, prices or personal-data flow.
- **AST-RTL-004**: 0.468 × 0.342 × 0.316 m faceted small-goods case with eight external ribs, divided nested carrier and a seated lift-off lid. Closed, lid-parked-open and explicit detached carrier-handling derivatives remain one design. Nothing is placed inside the two tray compartments. No closure seal, latch behavior, food compatibility, load rating or quantity is implied.

## Editable and native files

`source/AST-RTL-003.blend` and `source/AST-RTL-004.blend` preserve named semantic parts, ownership empties, metric UVs, small editable edge modifiers and packed material maps. `exports/*.glb` consolidates evaluated geometry by shared material and actual fixed/lid/carrier ownership. The source is Z-up, front −Y. Native GLB maps source (x,y,z) to (x,z,−y); actual node transforms are authoritative.

`source/build_retail_work.py` reconstructs both designs from original inputs only. The new terracotta enamel is regenerated from the shared original `materials/retail/draw_textures.py` before palette loading. The dependency manifest includes every common helper-loaded texture, including unused roles. The original parcel pictogram is seven encoded geometry strokes with no font or external artwork. No `.blend`, GLB, QA output or rendered image seeds reconstruction.

The editable source projects metric UVs on raw semantic faces before edge modifiers. The evaluated export deliberately reprojects every face by its dominant evaluated normal axis, using the unchanged material tile scale. Bevel-face native UVs can therefore differ from direct modifier-interpolated source UVs. Independent review retains that direct comparison and separately verifies expected native corner values under this declared policy.

## Physical proposals

Per-ID manifests and `marker_api.json` separate physical surfaces, support polygons, detached ownership, use-space proposals and placement origins. The container foot is an actual down-facing eight-vertex contact patch; the lid locator rim rests on Z0 in the parked derivative. In the handling derivative the tray is explicitly externally held and unsupported. The carrier first lifts vertically from its real bearing rails after the lid clears; its path is not a retained mechanism, force simulation or runtime animation.

`collision_proposals.json` supplies detailed semantic convex parts and optional body subsets. No assembled hull fills the open bench storage, case lower cavity, two carrier compartments or grip openings. Bench: 26 detailed / 15 optional shapes. Case: 48 detailed / 40 optional shapes; its eight fine ribs are omitted only from the body subset. Contact/use markers remain separate. Engine cost and actual body/reach fitting remain unmeasured.

## Scope and evidence

The reference images were inspected directly. R070 is a historical 12 × 12 m allocation proposal only. Actual room polygon, floor support, aperture, moving door/pockets, ownership and activity slots remain unknown and protected. The proposed bench/context transforms do not alter capacity, shop inventory or gameplay.

Independent geometry, source/native and source-only reconstruction review precedes final images. Camera preflight reads actual GLBs and must pass for every view before a serialized capture. Ordinary 640 × 360 views and higher detail views use inspection-only floor/light/camera aids; they do not claim original game visuals. Frozen hash receipts identify exactly which source/export/script produced each image.

## Completed r05 checks

Both components passed the independent physical review: actual source/native contacts and markers, whole support patches, real useful void volumes with blocked controls, full case/locator containment and complete detached paths from the true closed state. The carrier has at least 22 mm clearance to the actual eight-sided inner shell; the lid locator has at least 6 mm. Omitted-detail distance bounds remain separate from material thickness: bench face/strokes/control/marks are 8/11/16/19 mm from the retained body union; case ribs are 6 mm. These are geometry proposal limits, not body or runtime acceptance.

The exact 13-original-input clean rebuild passed: four native GLBs reproduced byte-for-byte and both editable sources reproduced semantically with packed material identity. The 94,305-byte `qa/retail_work_source_only_inputs.zip` contains only those original inputs, including the new enamel generator and every common helper-loaded texture.

Six actual imported-GLB views passed all camera preflights and completed in one serialized Eevee capture with frozen source/export/script hashes. See `qa/render_evidence.json`, `qa/render_launch_r05.json`, `qa/author_visual_review.json`, and the six PNGs. The ordinary-height case-on-bench view includes eight native triangle witnesses, one at each contact-polygon corner. Native UVs intentionally use the explicitly declared evaluated-face metric projection; the independent direct-source difference is retained honestly and the expected native corner values pass.
