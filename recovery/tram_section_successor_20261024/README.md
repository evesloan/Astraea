# Tram section successor — source candidate, not an operating tram

This additive namespace preserves the independently retained `c2d7383311d3f52574a150c56bac6a9b6e3a0c3e` source and all earlier native revisions. No main hook, original model, shared controller, admission flag, persistent actor or capacity is changed. Root alone owns engine execution and publication.

## Physical change

The actual selected Group7 owner `G7C6_D09_ComposedEdge` occupies X42.11–45.423008, Y52.5–55.889999 and Z±13.4243. The previous X44.5 middle leg intersected its metal fixture, three foliage materials and bark (88/195/207/645/222 triangles). These installed sources remain unchanged and visible. The named section moves only the middle route leg outward to X47.5; the curved CENTRAL stop and exact previously connected bridge are unchanged. This adds six metres to the route. Other stop identities, existing lift pits/cabins, floors, protected lower route and capacity remain unchanged.

The candidate contains 363 authored section parts, 42 receiver records and 76 full actual bearing footprints. At nominal source cursor454.7, the D10 header moves 0.5 m along the route to455.2 so both complete pads bear on retained `D10_authored_atrium_terrace` and `D10_atrium_circulation`; adjacent header spans become8.5/7.5 m. Source ownership is established; structural capacity is not thereby accepted.

Both protected envelopes remain4 m wide and4 m high. Lower protected Y52.55–56.55 is unchanged; upper running Y56.1–60.1 is unchanged. Rail head55.74 and soffit55.55 remain unchanged. D10 bearings use the actual underside60.76. No hull/slab cut, height adjustment or guard reduction is used.

CENTRAL body position is(-3.1851063986930437,56.1,-78.64857410214987), yaw1.1290098598838334, at cursor388.5155860482161. It comes from the actual two-bogie/chord pose, not a straight centerline assumption. Bridge origin(-4.250841579267747,56.1,-76.39526638263465), yaw1.1290098598838334 and reach1.3852191498493105 are unchanged from the protected connected r002 bridge. Fixed hinge/knuckle source remains exact; the longer moving panel/tongue from that source is reused byte-for-byte.

## Actual controller successor

`assembly.gd` creates one new empty assembly; it refuses a surviving Group4 owner. It retains the original five lift bindings, source024 vehicle factory/collision policy, original portals/restraint, and the AFT_MIDSHIP upper successor. Only named old guideway/receiver/central-end members are replaced. Original motor loaded-cart/caster paths are inherited unchanged through `motor.gd` and can only attach to the caller's original cart. No new cart or passenger is created.

`boarding.gd` uses explicit **PORT** identity for curved CENTRAL,15 stationary physics frames and the original strict distance<0.005 m/yaw<0.001 rad criteria at the actual body. Eight original CENTRAL fixed barrier-receiver members are rebound by the exact bridge transform. Existing phases, door/clamp/occupancy interlocks remain. The expanded bridge query retains the original end margins,2 m height and2.22 m width, extending its longitudinal range to[-0.07,1.462626557256718] m. It detects the new panel area instead of relying on the old1.17 m end.

All motion, boarding, joint and assembly admission defaults are false. `check_controller.gd` temporarily authorizes boarding on its isolated test instance only, after the physical dock checks, to exercise the actual curved PORT cycle; it never instantiates a motor or moves a passenger. That local test permission does not change production selection.

## Evidence and sole-engine handoff

`SOURCE_GATE_FINAL.json` is the selected source result. It checks exact triangles from28 selected actual owner instances: core/atrium/nursery, eight structural bearing pairs, overlapping Group7 sources selected from all88 retained headers, D09/D10 galleries, adjacent retail shell/portal and retained CENTRAL station/stair/receivers. Both four-metre envelopes are retained. Complete source024 body, closed portals, restraint stroke, console and articulated bogie/wheel components are bounded over every CENTRAL pose interval. The proof uses exact per-interval body and bogie transforms with conservative translation/rotation padding and full wheel-spin bounds. Only the three intentional wheel-contact rail/web ribbons are excluded from the body-envelope neighbor test; supports/shoes remain included. This is bounded selected-source clearance, not whole-ship runtime admission.

Earlier source receipts record deliberately conservative failures: uniform Y inflation on a constant-height path; then a solid car box filling empty wheel space; then whole-allowed-range steering instead of actual per-interval articulation. Final validation corrects the test representation, without changing any shoe/rail, weakening any four-metre guard or ignoring a conflicting owner. `geometry_r001` records the unresolved preliminary D10 bearing; **only geometry_r002 and the `_r002` runtime asset/plan/poses are selected**. Unsuffixed preliminary assets are unselected history.

Root commands, from repository root (substitute the retained engine paths):

```sh
godot --headless --path Game --script res://tram_section_successor_20261024/check_controller.gd
godot --headless --path Game --script res://tram_section_successor_20261024/check_controller.gd -- --negative-control
blender --background --python recovery/tram_section_successor_20261024/build_native.py -- --output recovery/tram_section_successor_20261024/native/Tram_Section_20261024_r002.blend
```

The first command must finish with zero failures/exit0. The intentional negative control must exit1 and print FAIL without a later PASS. Native output must be a new path; the helper has not executed Blender. `build_native.py` preserves all original native files, packs source textures and produces editable derived geometry with clear collections and provenance.

`installed_gate.gd.audit(candidate_assembly, actual_selected_ship)` is the subsequent integration gate: actual closed original motor/bogies/console/restraint are required; exact contact shapes are queried at the authored poses against the caller's installed world without moving the vehicle/player/cart. It refuses a disconnected fixture, preserves live transforms and does not admit motion. Full selected-world visual-only neighbors, loaded-cart/caster behavior and a physically moving passenger remain separate gates. The known original caster impulse is not claimed solved.

The old connected static r003 receipt (534 checks, actual source024 factory) remains valid evidence for the unchanged CENTRAL platform/apron/bridge/body floor; it is not retroactively a pass for this new controller or route. Current engine tests, native visual review, structural capacity, moving-passenger scenic experience and performance are pending. No new FPS, playable build or final art claim is made.

## Exact ownership and future production hook

Only `Game/tram_section_successor_20261024/` and this recovery directory are new. `CONTRACTS.json` pins candidate-owned files and the actual reused prerequisites; `PACKAGE_MANIFEST.json` lists complete changed bytes/hashes. Global source contracts and main remain unchanged. A future root-owned main adapter must replace the **single** Group4 constructor at its normal before-budget boundary, retain original persistent cart/player and existing light-budget/controls/information bindings, then call the named assembly/motor. Do not create a second Group4 tree or adopt this namespace merely because a bounded test passes. Existing loaded, caster, stationary, door and admission gates remain authoritative.
