# D17 next supported-frame candidate

Read-only bounded planning pass, 2026-10-05. No project/catalogue edit, build, import, engine, Blender, commit or helper launch. The sole output is this handoff. World coordinates: X right, Y up, Z aft; metres.

## Recommendation

Resolve **one braced Royalty longitudinal support frame at X108** before trying to carry either whole wing. It reuses both already source-seated footings, has two explicit end bearings, and avoids inventing a 47–58m court transfer. This is the smallest concrete framing candidate with retained contacts at both ends. It is not a traversable route, a completed support design, or permission to compile any of the16 held room floors.

Proposed primary member bounds, for a bounded source-fit trial:

| Member | X | Y | Z |
|---|---|---|---|
| Royalty fore pier |107.6–108.4|−0.45–100.56|29–30.2|
| Royalty aft pier |107.6–108.4|−0.45–100.56|49.8–51|
| Longitudinal transfer |107.6–108.4|100.56–101.76|29–51|

The transfer is1.20m deep,22m overall, with20.8m between support centres and19.6m clear between bearing footprints. These are proposed geometric bounds, not calculated structural sizing. Its top reaches the reserved D17 slab underside101.76; it does not project into the normal roof or Royalty upper. The strip stays wholly inside the candidate790 footprint X94–118/Z29–51. It must not be generalized into14m/10m unsupported transverse room-floor cantilevers.

Exact contacts:
- Fore pier bottom: entire0.8×1.2m top face of AST-RES-005 / D17_SeatedHullFooting_0, Y−0.45, X107.6–108.4/Z29–30.2
- Aft pier bottom: entire0.8×1.2m top face of D17_SeatedHullFooting_1, Y−0.45, X107.6–108.4/Z49.8–51
- Transfer bottom:0.96m² on each proposed pier top at100.56. No gap, floating head or edge-only bearing is intended
- Both retained footing bottoms already seat on AST-HUL-001 / HUL_LowerBand_00, actual editable polygon56. Source QA has81 rays per footing,0.96m² projected contact per footing and minimum wedge thickness0.34999876m. Do not replace the wedges with flat bases

## Evidence and bounded frame order

The existing parent_outer_support_census.json tested both0.8×1.2m vertical footprints in16 slices from−3.2 to112 and found no non-hull contacts. Existing seated-contact/source-export QA covers the delivered footings, not the proposed members.

This pass separately compared the **entire transfer plan rectangle X107.6–108.4/Z29–51**, not only its ends, against all1000 historical guest,200 crew-bank,100 shop and161 historical programme envelopes. All four categories had zero positive-area overlap. The same full-category test also confirms the X100/Z±24 footprints remain allocation-clear. No lower guest, crew or programme allocation needs relocation for the proposed X108 strip.

Parent subsequently completed two main-scene checks, whose receipts were read in this pass:
- d17_royalty_transfer_census.json: exact X107.6–108.4/Y100.56–101.76/Z29–51 transfer box, zero static contacts, after90 physics frames with an unsaturated1024-hit limit
- d17_royalty_frame_strip_census.json: the entire X107.6–108.4/Z29–51 strip fromY−0.45 to101.76 in16 unsaturated height slices, all clear. The receipt's top-level bounds describe the transfer; its full_height_strip_slices hold the lower frame checks. These engine runs were performed by the parent, not this worker

Therefore a **geometrically rooted single deep bay is feasible as a source candidate**, with in-plane bracing fitted inside the already-cleared strip. It need not be represented as two isolated101m posts. Do not call it load-accepted or laterally stable solely from that geometry.

Next frame order, confined to this one bay:
1. Author the two primary pier/chord members on the exact retained footing top faces above. Preserve both source-seated wedges and all existing objects
2. Fit a repeated open braced web between the chords, wholly within X107.6–108.4/Y−0.45–100.56/Z29–51. Join every web/rail end into a chord or another positively rooted node, with shared actual mesh coordinates and positive face/volume contact. The full strip census permits this bounded source-fit without inventing further support stations. Panel spacing/member sizes remain source-design choices, not evaluated engineering sizes
3. Seat the1.20m-deep transfer on both chord heads atY100.56. Each end has0.96m² face contact;19.6m is the remaining clear bay. Verify that the web joins genuinely meet the primary members after export
4. Prove source/export identity, manifold/positive-volume members, preserved existing objects and exact rooted contact graph. Preserve the continuous future-bearing top at101.76, but add no floor yet. The beam's0.8×22m top is17.6m² of potential slab-bearing surface, not an assertion that a528m² room is supported
5. Stop this bounded frame delta. The next floor-enabling design is **one transverse bay with a second rooted bearing toward the X94 entry edge**, plus edge protection; no such second bearing is proved here. Do not silently turn the X108 spine into a14m west/10m east cantilever. Keep all16 floor records, commons portal adoption and Royalty upper/stair/lift interfaces held

In-plane bracing does not establish out-of-plane restraint, axial/buckling resistance, connection capacity or footing/hull load capacity. Those remain separate design/acceptance gates. Any braces or second support lines outside the cleared strip need their own bounded contact and allocation checks; no existing owner is authorized to move.

## Why not begin with the X100/Z24 junction

X100/Z±24 really is clear in the recorded0.8×1.2m shaft censuses and all four allocation categories. Its actual base target is HUL_LowerBand_00, with runtime corner heights approximately−1.947561 and−1.843218. It has no delivered source-seated footing yet. Clearance there does not root a20m projection back to portal X80 or24m to standard edge X76.

The tempting shorter connection from retained commons pier(94,11.5) to(100,24) is not automatically an escape: its centreline crosses the retained diagonal side wall at approximately X94.48649/Z12.51351. A below-floor transfer atY100.56–101.76 intersects HC_ProfileWall_D16_1_5 there; an upper transfer below106.26 encounters the corresponding D17 wall. The fore mirror has the same issue. This would require a separately resolved bounded wall/interface change; the accepted portal opening atX78.5–81.5 does not authorize it.

Verified retained source references: HC_PierExtension_3 at X93.68–94.32/Z11.18–11.82/Y92.16–106.26; HC_Bearing_3_101.76 at X93.664–94.336/Z11.164–11.836/Y101.58–101.76; HC_PerimeterTransfer_101.76_1 at X64–94/Z11.85–12.15/Y101.40–101.76. These bounds come from the current builder and raw glTF accessors, with the established world offset(63,84,0). Existing materials/walls/cover/arrival/stairs/lift are preserved; their proximity alone is not a new beam seat.

## Retained evidence and hashes

Catalogue root: /workspace/shared/astraea-catalogue-continuation-20261002
Godot root: /workspace/shared/astraea-godot-production-20261003

Read: project AGENTS.md; docs/D17_STARBOARD_HOUSE_SECTION_PLAN.md; all three interface/added/alternative support censuses; assets/d17_house_platform/HANDOFF.md, source/section_contract.json and QA receipts; upper-commons builder/contract and raw GLB bounds; lower-hull builder/contract; all four allocation sources. Parent's new qa/verify_allocation_footprints.py and allocation_footprint_regression.json were inspected, not rerun or edited.

Current source contract SHA256: d9011f57412215ff04ef95c0a64e6275799b303620a68578649834548385d5d3
RES005 source SHA256:25b735b9e372306297eef813d491ceb3ba7f85b011c2329fcdba93f9c4d97472
RES005 export SHA256:ff8749f805b8b668a8a32009a0bd5c83bd069e77194770f3bddc5dc2ae29d621
HUL001 source SHA256:9bd075271f0049d6c69b9d307f51578acc101b0c518f959507221d573bc8c0aa
HUL001 catalogue/runtime export SHA256:0a53fd2357fe1ca24b350bf53f0ee9bc2d495e8306f581c1ac13bfb685cd7fd0
Retained COM003 runtime export SHA256:d2ebe0a3a980cb283a4dc8909d07609d112dcbca196d3edbbf7bf47f1fcc9125
Outer-support census SHA256:09c0af78f13819a5bb9b258d2a87644f09b35da726583967a5f3bd4065f1a8f1

No source authoring, source-level new-member collision/round-trip verification, load/bracing analysis, route/cart/species/occupancy or visual acceptance was performed in this pass. Parent-supplied actual Godot box censuses are explicitly distinguished above.
