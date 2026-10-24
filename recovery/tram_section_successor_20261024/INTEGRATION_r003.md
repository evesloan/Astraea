# Normal-constructor integration adapter r003 — unselected

Prerequisite protection: `4e547c4b21e16eeb621a3fe5b756618b12eb340b`, independently read back49 files/14,623,360 bytes. Root's isolated curved-controller fixture passed29 checks/exit0; its negative control exited1 without a false PASS. Root generated the new editable native successor,4,776,856 bytes, SHA256 `a180eb15aa5a9238321b79123d4a6155064d94ef2d2a6381b9a1e5fdd0b812ba`. None of those protected files is rewritten by this r003 addition.

## Exact integration boundary

The selected Tidal-arrival ship inherits22 additive successor classes above the consolidated constructor. They override `_construction_step` (some also room helpers), with no intermediate `_ready` override. The consolidated constructor's `_ready` already shadows the original base `_ready`; calling that base as well would duplicate construction.

Root's named most-derived ship can therefore extend the current Tidal-arrival ship and copy **only** the exact consolidated `_ready` function. Replace exactly these two calls, without modifying the surrounding awaited labels or budget configure:

```gdscript
if load("res://tram_section_successor_20261024/integration_r003.gd").before_budget(self)==null:return
await _construction_step("group4_integrated_receiving.gd")
lighting_budget.configure(self,player)
if not load("res://tram_section_successor_20261024/integration_r003.gd").after_budget(self):return
await _construction_step("group4_integrated_receiving.gd")
```

The literal labels are required by `court_completion_integration_20261022/ship.gd`: the first installs its lighting-budget script while sources are empty; the second validates that same owner after configure. Every other dynamic district hook, later received-section installer and deferred builder remains inherited. Do not rename labels, cache-remap scripts, clone the entire inheritance chain, call both constructors or swap a live assembly.

`integration_r003.gd` preserves the original exact pit guard, seven active source-package predicates, north-stop/shared-pit predicates and terminal presence predicate. It creates the r002 assembly once at the normal construction boundary, restores canonical `ShipSpace/Districts/Group4Completion`, then attaches the **original** persistent cart to the original loaded restraint/controller through the named route binding. It does not clone or move any persistent actor or product. Across phases it verifies original player/cart/four products/order/handle identities; within each synchronous phase it verifies unchanged actor/cart transforms. It deliberately permits normal physics settling during the retained intervening yield.

The after-budget phase calls the retained controls and station-information builders once, using the actual original player, cart, motor, gates and current light budget. The same handle instance receives the original scoped guard/restoration path. Exactly one car light is registered, preserving the five station cases/calls and eight car buttons. Default assembly, boarding, joint and motion admission remain false. Failed preconditions return null/false, set `tram_section_adapter_error`, and the checked root call sites stop `_ready` before it emits construction completion/readiness.

## Root-owned experimental entry

Root created these outside helper ownership; their actual hashes are captured by `SOURCE_REVIEW_r003.json`:

- `res://scenes/ship_tram_section_candidate_r003_20261024.tscn`
- `res://scripts/tram_section_integration_20261024/ship_r003.gd`

The default project main remains the existing Tidal-arrival scene. r003 is an opt-in installed-world test entry, not a selected playable build.

Root's single monitored headless check (only after source preparation and available capacity):

```sh
godot --headless --path Game --script res://tram_section_successor_20261024/check_installed_r003.gd -- --ship-scene=res://scenes/ship_tram_section_candidate_r003_20261024.tscn --ship-sha256=baf75976eaed57ff83c17dcd0c603b854d574366addb06452750e9c3b3d6a32f --script-sha256=dfd7110e690cf95b80b44ae5ad49993f1f34c1b1bbee989ee478b59b11e5ef0c --startup-limit=300 --report=/tmp/astraea-tram-installed-r003.json
```

The checker refuses missing/changed entry hashes before constructing a world; it does not implicitly launch the current default scene. It waits for actual `runtime_ready`, completed `ReceivedSectionInstallation` and an empty deferred-builder list, failing promptly on `tram_section_adapter_error` or its bounded deadline. It verifies canonical single ownership, the real original actor/cart/product bindings, exact portal decomposition, articulated bogies/wheels, explicit PORT/15-frame docking and all admission holds. It neither changes actor/cart poses, freezes their bodies nor changes world pause for its test.

It then calls the protected `installed_gate.gd.audit` using the actual constructed world, original motor, controls and contact shapes. Queries do not move the car or passenger. No test enables production motion/boarding/joint readiness. Its full-world result is **not yet run** by the helper and must not be inferred from isolated29-check success or the source triangle/body-envelope proof.

The gate does not accept original caster impulse, loaded-cart dynamics, moving passenger/scenic experience, structural capacity, whole-ship visual fidelity or performance. Any installed neighbor conflict must be reported with its source owner; no geometry or guard may be silently omitted to turn this check green.

## Files and verification

`INTEGRATION_CONTRACTS_r003.json` pins the unchanged r002 contract, actual current inheritance chain and original pit/constructor/actor/control dependencies plus the two r003 scripts. `SOURCE_REVIEW_r003.json` records exact chain/method ownership, confirms only two checked-call substitutions in root's new `_ready`, and verifies reused nested source pins. `PACKAGE_MANIFEST_r003.json` covers only this additive r003 handoff. Global source contracts, main and protected r002 bytes are unchanged by the helper. Engine execution and Git publication remain root-owned.
