# Group4 additive receiving module003

Uninstalled source construction only. This adds receiving members to frozen port successor002; it replaces no rail, station, moving body, floor, controller or protected source. Whole Group4 remains open.

## Supplied

- 244 editable members, one compact `AST-TRM-G4-017_receiving_module.glb` and native Blender
- 52 complete positive-area contacts on actual named D09/D10 compiled slabs
- Four formerly ambiguous core-end contacts moved1m inside their exact retained D10 core owners, each with0.0864m² contact
- 22 overhead header sites on the actual central/tie receivers; bottomY60.18 preserves the reserved running topY60.1
- South-tie D09_aft_route feet/cantilever trusses atZ84 and92 where D10 narrows toX±4 and provides no outer-port receiver
- Two continuous underweb receiving girders using the frozen route vertices through the corners; soffitY55.55 retains3.05m lower-axis clearance
- 62 small receiving shoes close actual frozen hanger-to-web gaps (42 trunk-core and20 forward/aft station-carrier shoes), with positive contact proved against the original members

All four core-end owners are explicit: D10_forward_public_core_floor, D10_fore_midship_public_core_floor, D10_aft_midship_public_core_floor and D10_aft_public_core_floor. AtX−3.9, their new pad centres useZ−413,−253,+291,+451. These are new members inside already present floor, not moved existing structure or floor cuts.

## Verification

Finite/index/bounds checks, zero degenerate triangles and native/world export agreement. Exact triangle-contact refinement finds no unintended adjacent contact across44 retained route-source instances plus15 actual Gallery fittings. Complete positive pad-area clipping uses the current compiled floor triangles; intentional receiving joints are declared rather than broadly exempted.

Existing frozen body poses are reused without sampling new routes. Ties retain0.20m horizontal margin and corners0.15m. Full-body-box broadphase found only low shoe candidates; refining all39 actual vehicle-part vertical bands removes those candidates. Shoes end below the vehicle floor, while actual wheel bounds retain the same horizontal margin. Nominal underside-wheel gaps are0.03m at underweb girders and0.015m at the south seat. These are construction gaps, not dynamic steering/deflection acceptance.

All central receiver vertices remain within1.891m of the exact protected polyline's2m-half-width strip. Central X40 members remain insideX38..42, preserving the full1m separation to GalleryX43..46.5. All actual Gallery bounds and hashes are retained. No lower4m-axis intrusion is present.

Three actual native studio views reviewed: central headers/rail contacts, a core-end receiving shoe and south-tie cantilevers. The frozen guideway appears only as unsaved render context and is not duplicated in module exports or native outputs.

## Root-owned gates

All five successor002 floor/pit proposals remain uncut and root-owned. Central17.6m² recess owner is D09_atrium_circulation; outer-port fore-midship17.6m² pit belongs entirely to its new receiving annex. Lower annex/foundation/fill, central secondary-stair receiving and all primary hull/load/capacity/deflection/vibration remain open.

No operating tram/door/gate/bridge/bogie/clamp or NPC transit is supplied. Reuse existing commons_lift/AST-CIR-003 and E/RMB controls as recorded in successor002. Normal boarding/arrivals, remaining destination links, body/species, CRT, lighting and GPU acceptance remain unfinished.

## Bindings and reproduction

MODULE_INTERFACE.json records exact receivers, shoe joints, source ownership and root gates. SOURCE_RECEIVING_CHECKS.json, BODY_RECEIVER_CLEARANCE.json and SOURCE_VISUAL_REVIEW.json define the bounded evidence. FROZEN_RECEIVING_MODULE.json binds the stable file list.

Regenerate only in a separately versioned work directory, preserving this frozen slice. `plan_receiving.py`, then existing installed Blender `blender -b --threads 1 --python build_receiving.py`, then `OPENBLAS_NUM_THREADS=1 python validate_receiving.py` and `python check_body_clearance.py`. Source pictures use `render_source_review.py` without saving native changes. No Godot/import/full build or Git/ref/publication operation was run by this helper.
