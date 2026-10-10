# Forward staff upper shaft — held physical interface slice

Upper travel remains disabled. The current production lift preserves forward_staff_lift_001, original five destinations [0,6,12,46.2,52.5], cabin/buttons/gate IDs and working lower interfaces. D13–D17 temporary shaft-mouth closures and abandoned west-mouth closures remain physical. No upper call buttons or operation are enabled.

37 unchanged retained AST-STF-G3-003 native upper_shaft parts now form the enclosure from Y55.6 to105.2. One missing-only top cap at Y105.2–105.34 adjoins the retained D17 service-stub roof at X-23.18. Five fixed sills close the 0.01m cabin/front-floor clearance; each has0.192m² contact with the retained receiving floor. Geometric contacts establish fit, not certified primary structural/load capacity.

GPM_STF_NewCap is identified in the exact retained native predecessor. Its six oriented surface areas reconcile to40.09467768268951m² in the runtime asset. Exactly12 cap triangles are removed from HOME_BATCH_062_ASTRAEA_staff_bluegrey_paint. The other140 triangle point sets in that batch, UVs/materials, every other runtime batch and all original files remain retained. The new native cap-only successor and exact triangle-index map make reconciliation reversible. Adjacent wall tops and D09 ceilings are preserved.

ForwardStaffUpperEnvelope.blend / AST-STF-009_upper_tidal_envelope_r001.glb contains43 meshes:37 retained shaft parts, one top cap, five sills. ForwardStaffLowerCapOnlySuccessor.blend exports one named batch successor. Both reopen/export byte-identically. SHAFT_INTERFACE_PLAN.json records original hashes, native cap bounds, exact removal map, all37 original part bounds and five sill/gate identities.

Five existing AST-DOR-003 / lift_gate.gd interfaces are installed at the unchanged source centres [-23.08,Y,-490], yaw-PI/2. Their persistent IDs are D13_forward_staff_lift_gate through D17_forward_staff_lift_gate. Gates remain closed and reject open requests without a present cabin. The retained collision family has a0.005m meeting seam; ordinary central capsules are blocked. This is not pressure/hygiene sealing acceptance. Original five gate IDs remain untouched.

Only one additive existing lower_staff_network.gd build call installs this slice. commons_lift.gd and its Star Atlas pin stay unchanged from the independently protected panel checkpoint. Runtime cap reconciliation replaces the named mesh and refreshes physical contacts; no source file is overwritten and no geometry is bypassed by disabling collision.

The next activation gate is explicit: bind the retained ten-stop controller/cabin to these five upper gates/sills while preserving the original five IDs; reconcile only the five temporary mouth closures after interlock and moving cabin-gate/frame clearance verification; then perform bounded actual upper travel and obstruction checks. Full structural/load, species/cart/hygiene, detailed traversal and final runtime visual acceptance remain open.

Native source views and failed source/engine attempts are retained. No exhaustive ship route audit, automatic watcher, extra workers or environment restore was started.

Actual-main PASS:54 shaft-wall rays, three blank-front rays,20 closed upper-gate rays, five central capsule barriers,20 sill rays, exact old-cap removal/new-top cap contact, inflated primary cabin envelope with zero static intrusions; all84 D13–D17 floor/capsule checks, four support/external-contact checks,2000 door sweeps/two cycles preserved. Import3.927s; fixed60Hz simulated test43.210s. Full suite, upper moving-gate travel/obstruction and final runtime visuals not run.
