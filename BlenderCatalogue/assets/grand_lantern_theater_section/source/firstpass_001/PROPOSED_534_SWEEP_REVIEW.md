# Proposed 5.34m moving assembly: continuous source-envelope review

Status: **PROPOSED ENVELOPE PASS, NOT APPROVED OR AUTHORED MESH ACCEPTANCE.** No hard source contact was found. No Blender, Godot, engine process, export/import, runtime or shared-source edits were used. The original theater saved-source hash remains c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5.

## Exact candidate and reservation delta

The source-owned 6×6 shaft reservation remains X[-44.5,-38.5], Z[-124,-118]. No hole, floor or foundation cut is proposed. The original nominal 5×5 platform reservation remains X[-44,-39], Z[-123.5,-118.5].

- Proposed actual platform: X[-43.99,-39.01], Z[-123.49,-118.51], 4.98×4.98m, centered inside the existing reservation. Its 10mm gap to the fixed sill does not move any fixed source.
- Proposed maximum width of the complete bounded assembly: **5.34m**, X[-44.17,-38.83]. This is a separate motion envelope, not the moving floor or a new walking-floor polygon.
- Conservative full moving horizontal envelope: X[-44.17,-38.83], Z[-123.49,-118.51]. Area 26.5932m².
- New lateral reservation strips outside the old 5m rectangle are exactly X[-44.17,-44], Z[-123.49,-118.51] and X[-39,-38.83], Z[-123.49,-118.51]. Each is 0.17×4.98m; total additional conservatively reserved motion-plan area **1.6932m²**. This is not added floor area. The conservative box omits 10mm from the old rectangle front/rear and therefore has a net bounding-area difference of 1.5932m²; do not confuse that with the additional side strips.
- The presently known gate-header protrusions alone occupy smaller side strips at Z[-123.455,-123.255], total **0.068m²** outside the old 5m rectangle. The full rectangular reservation is deliberately more conservative so that chassis/roof/support geometry may be bounded without pretending those gaps are solids. It still needs parent approval.
- Complete permitted local moving vertical bound for this proof: h[-0.18,+3.60] relative to cabin floor. Floor motion is continuously Y69.5…84, through 78. Minkowski sum yields **Y[69.32,87.60]**. This covers the optional 3.0m-clear cabin roof (+3.31) and also a 3.4m-clear gate/header (+3.60); it does not approve either height choice.

Every future leaf, seal, hanger, frame, cabin, chassis, rail/shoe moving part must remain inside this box for this proof to apply. The earlier provisional **5.40m rail/shoe allowance is not covered and is withdrawn from this candidate**. Rails/shoes need a real section that respects the 5.34m bound, or a separate new envelope proof and approval. No enlarged envelope is implicitly authorized.

## Continuous proof from pinned actual source geometry

The test reads `source/geometry.json`, representing the actual retained source validated by `qa/editable_source_reopened_report_001.json`. For every non-preview part, it computes the actual vertex AABB and demonstrates a strict separating coordinate interval against the entire swept box. All **6,968 authored parts** are separated. Therefore none of their vertices, edges, faces or bounded solids can intersect the proposed moving box at any intermediate height. This is a conservative continuous interval proof, not sparse stop/sample testing, and it needs no triangle inference once every AABB is disjoint.

The broad `D11_COMPILER_PREVIEW_NOT_EXPORT` slab does intersect the box. It is the single explicitly `preview_only` object excluded by the source adapter and must remain absent from source/export/collision. Treating that preview as live floor would invalidate the fit.

Additional independent polygon checks:

- All **4,564 parts of the eight upper surface records** have zero positive-plan overlap. Both D12/D13 foyer records include their fixed sills; these are checked rather than ignored.
- All **seven approved D11 foundation polygons** have zero overlap with the whole 5.34m rectangle. The closest is the shaft-foot U-shaped polygon, with **80mm** separation. Foundations occupy Y69.26…69.50 and thus overlap the moving envelope's lower vertical band, but the exact polygon exclusion keeps them horizontally disjoint. They are not assumed absent merely because the former 5m platform was excluded.
- The D11 compiler floor candidate's outer-boundary overlap is 26.5932m², and its shaft-hole overlap is the same 26.5932m²: resulting **solid overlap is zero**. Distance to the candidate floor hole boundary is **330mm** minimum.
- The six-meter shaft-hole edge margins are **330mm west/east and 510mm front/rear**. The sidewall thickness reduces real lateral clearance to **80mm**. Rear wall clearance is **260mm**; solid jamb-back clearance is **260mm** for the full box.
- The closest actual retained parts are all three fixed sills, each **10mm** away in Z. This is the limiting geometric gap, not the sidewall width.
- Proposed new stationary landing-gate frames at each stop have Z[-123.735,-123.535], so they are **45mm** forward of the full moving box. Their new supports/attachments are not built; they must remain forward of that boundary or be separately checked. Their actual source meshes cannot yet be credited as passed.

Foundation authority was verified against `qa/PARENT_SOURCE_REVIEW_20261006.json`: the approved proposal SHA256 is `f9145941899c3a6335072827aeef7ad87cf7d1311e2234d57836bd5a46b7927b`, geometry SHA256 `90406045c5c23e52af1850bba8ea3088cb672de072afa47a7f5e6feb39927429`. All inputs are hash-bound in the report.

## Source/import precision and the 10mm sill gap

The source adapter writes float32 Blender coordinates. The earlier reopened-source report's zero coordinate error compares `mathutils.Vector` float32 representations; it does not establish zero difference from original double-precision JSON. Independent conversion measures:

- Maximum JSON-to-float32 component error across actual theater source: **0.012207mm**.
- Maximum corresponding component error near the lift: **0.006104mm**.
- Quantizing both source vertices and the entire proposed envelope to float32 leaves no overlaps. The limiting sill gap becomes **10.002136mm**.
- A separate float32 local-coordinate plus float32 world-root addition produces the same 10.002136mm gap for the platform front.

Thus float32 coordinate precision by itself does not consume the 10mm gap. As a conditional future acceptance budget, expanding every actual source AABB and the proposed moving envelope by **1mm each** still yields zero overlaps and leaves **8mm** at the sills. This is a proposed maximum combined geometry/placement error budget, not a measured new import result.

The new derivative has not been exported or imported. Collision margins, collider inflation, root placement, runtime motion tolerance and physics contact behavior remain unmeasured. Their total intrusion/error must be bounded below the remaining gap, and actual imported vertices/colliders must be measured. A 10mm visual mesh gap is not permission to accept a 10mm-or-larger effective collision envelope. No promise of runtime freedom from catching/jitter is made.

## Pit, headroom and external limits

The source-only box starts at Y69.32 and ends at Y87.60. It clears the approved lower foundations and all existing upper authored parts throughout that interval. The shaft enclosure ends at87.65, leaving 50mm to its top *edge* for the conservative tallest bound. That edge is not a roof, buffer, guide bearing, motor or verified machinery ceiling. The selected 3.0m-clear cabin candidate itself would have roof top87.31, leaving340mm to that edge.

There is still no authored pit floor/buffer or accepted machine/rail support arrangement. Future below-platform parts below69.32, above-box parts above87.60, or width/depth excursions invalidate this proof and require a new bound. Retained external/current compiled scene objects and live collision census remain the parent's engine-integration gate. This report covers the exact pinned source, approved foundation and floor JSON requested, not unseen runtime geometry.

## Reproduction

Run `python check_proposed_full_sweep.py` from any directory. It reads only production source/contract files and writes only scratch reports in this directory. Full report: `proposed_534_full_vertical_sweep.json`. The existing `DOOR_LIFT_DERIVATIVE_PLAN.md` supplies the leaf widths, seal-aware strokes and 4.4m turning disk; its previous 5.40m guide/shoe suggestion is superseded by the explicit limit here.
