# Upper Horizon supported enclosure

AST-CMD-006 is a bounded editable structural enclosure for the existing D18 receiving foyer and fan. It adds no floor, furniture, programme, people, lights, controller or door mechanism. The complete ship remains unfinished.

## Current source

- 598 editable closed outward solids, 7,224 oriented triangles and 448 bounded runtime batches
- 28 logical single-plane glass panels form a shared observation ribbon around the fan sides, chamfered returns and rear wings; the foyer/service-adjacent sides remain opaque
- Two selected Z160–164 bays have an opaque top at Y107.42, exactly0.92m above floor106.5. Their single0.06m protective pane seats into0.36m-deep reveals with at least0.02m overlap. Clear aperture is Z160.10–163.90/Y107.42–111.03
- Main roof follows the supported fan. Rooted high shoulder ribs, eave and skin extend to|X|52/Z202; every new shoulder underside stays at or above113.40 and exterior tops at114.45
- All598 parts have explicit positive geometric contact paths to the retained six keel-bearing piers. The high shoulder joins actual roof-long flanges/webs reaching113.90; it does not drop to the112.08 low edge hangers in the viewing corridor
- The raised onward header lies Y112.28–114.20 and retains the8m open mouth. No sill, moving public door, pressure seal or new controller was invented

The thick upper frame and roof, perimeter profiles, continuous glazing ribbon and deep onward cheeks continue the existing fan and frame rather than substituting a rectangular hall. All25 existing fixtures retain their exact source identities/settings. The preserved core, receiving turn, full Z146 loaded-cart crossing, terminal service turns, wings and onward route have no new source solid in their protected volumes. Actual runtime travel remains a separate parent gate.

## Coupled005 revision

Adopt revised005 and new006 together. The only removed old source objects are ACP_Port/Starboard_GuardBack_01.008 and ACP_Port/Starboard_GuardCap_01.008. Each becomes a deterministically named fore_stub, low_bay and aft_stub. Their retained intervals are159.95272727272726–160 and164–167.20181818181817; the tiny fore stub is preserved. Both old toes remain whole and exact. All3975 unaffected objects, including all fixtures, markers and remaining meshes, have exact source geometry/UV/material/property hashes.

Every retained stub keeps old X/Y, old materials and affine source UV mapping; added cut closures are enumerated. Only central Back/Cap prisms change height. No002 file changes. Reversal is documented against catalogue commit62ecbc2c24d9a64c4999c8e7afc25bfc7ed3f4b8. The005 builder dispatches to the bounded revision once its contract contains low_sill_revision, so it cannot silently restore the high guards.

## View evidence

Bounded standing eyes use|X|32.7–33.1/Y107.95–108.35, starboardZ161.05–161.35 and portZ162.10–162.60. Seated diagnostics atY107.55/107.65/107.75 use those same X/Z boxes without adding furniture. All12 actual-triangle screens and5,294,322 sampled eye/ray pairs pass for the specified complete above-horizon cap/halo and crescent; the continuous whole-cone test has no opaque candidates. Each ray crosses both faces of exactly one intended pane. The shoulder clearance is0.535694m starboard and0.460736m port. Original higher-guard crops and inboardX30 cropping remain recorded.

This does not promise a full planet, every sky direction, panoramic visibility or a court view. Unchanged beams clip high-angle rays. Future pavilions/courts stay fixed. Finite D17 roof screening and conservative infinite-plane exclusions are separate; the roof clips low planetary rays and seated port fringe, while some very shallow negative standing rays can cross the plane beyond the finite hull. Source optics do not certify in-engine glass appearance.

The actual Godot spot_angle82 is a half-angle. All25 near-source82-degree exit cones clear new solids. The full downward onward cone has no raised-header intersection; distant wall receivers are reported normally rather than incorrectly required to be empty. The initial41-degree screening assumption was corrected before the final contact receipt.

The independent finish review found a coplanar old-walnut/new-metal sill top. The006 metal is now20mm above the retained005cap, with a similarly proud upper seal; qa/visible_finish_interfaces.json proves those two interfaces. This source correction preserves005 exact and has a final matching optical receipt at0b892eb5/70fd0d75.

## Proofs

- qa/preauthor_baseline.json: exact complete-manifest candidate check, immutable old hashes and four-part split contract
- qa/005_preservation.json and qa/005_exact_stub_audit.json: unaffected objects, exact retained stubs, UVs and added closure faces
- qa/source_export_validation.json: exact float32 oriented position/triangle/UV/material equality for005/006, closed outward geometry, bounded batches, marker properties and packed texture fidelity
- qa/architectural_contacts.json:598 individual join records, full paths,3856 explicit new-to-old contacts, protected clearances and fixture screens
- qa/actual_AST-CMD-005_triangles.json and qa/actual_AST-CMD-006_triangles.json: actual Blender triangles independently matched to exported geometry
- qa/view_screen/: paired baseline/revised source rays, future envelopes, current actual-triangle screen and disclosed failures
- qa/catalogue_registration.json:165 registered designs, preserved previous records and actual platform-baseline111designs/1690whole-model instances;006 remains unadopted

## Reproduce

Use Blender4.3.2 with two threads. Run source/revise_005_guards.py and source/build_upper_horizon_enclosure.py, then qa/verify_source_export.py and qa/verify_guard_stubs.py inside Blender. Run qa/verify_contacts.py with Shapely2. Source/prepare_enclosure_contract.py creates the initial roof-cell contract; it is not needed for normal geometry regeneration. View screening needs NumPy/SciPy; see qa/view_screen/README.md. The view code accepts ASTRAEA_CATALOGUE_ROOT and ASTRAEA_GODOT_ROOT for portable checkouts.

The immutable005 source baseline is read from Git into temporary storage, not restored over production. Reproduction asserts exact catalogue ID ownership before export. Reference pixels remain outside production assets.

## Still open

Parent owns import/atomic paired adoption, current249floor-owner and002preservation checks,96pier slices/30keel rays, full public/loaded-cart/service-door/core travel, default/effects-off seated and standing views, slow pans, full-window visual composition and fresh affected/aggregate tests. No preceding platform pass certifies this new revision. Broad species fit, furnishings, wayfinding, operating systems, complete hull/pressure continuity, engineering loads, capacity occupation, final art and RTX5060Laptop performance remain unfinished.
