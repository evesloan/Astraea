# Package A: actual tram / current player carry

## Current result and decision

The existing tram **does physically carry the current original player** through
its central curve, acceleration, cruise, braking and a real station stop.
The first extended run stopped at a strict displacement-screen failure after
FORWARD reversal. It did not drop the player or lose support.

A single controlled comparison then confirmed a one-physics-step visual/physics
pose mismatch in the original motor. Its proposed atomic/synchronized motor
successor **failed empty assembly and is rejected**. It was not integrated into
production. No additional tuning, retries or engine runs followed that failure.
The original current source and every production admission hold remain intact.

The separate fixed source016/017 intrusion into the protected four-metre D09
receiving volume remains the real production-integration blocker. None of these
bounded tests clears it, or loaded-cart acceptance.

## Exact retained attempts

- `runs/run-001`: original motor, original pre-node `physics_frame` observation.
  CENTRAL→FORE_MIDSHIP passed the configured first-leg checks. One supported
  moving-car spawn; maximum settled cabin-local horizontal drift0.096804 m.
- `runs/run-002-continuity`: same first leg and criteria, then FORWARD. Stopped
  during return acceleration at cursor54.976667, speed5.786667 m/s, physics
  frame6183. Drift0.100070 m exceeded the preset0.10 m screen. Player remained
  standing on the car within the original actor_aboard envelope. The tiny excess
  is not proof of unsafe riding. No pass was manufactured by relaxing tolerance.
- `runs/run-003-post-actor-baseline`: unchanged motor, observation at priority100
  after the original player, spawn anchored to the committed physics-body pose.
  CENTRAL→FORE_MIDSHIP passed. Drift0.096813 m. Node-to-committed-body translation
  reached0.100006 m at6 m/s; the player followed the committed physics platform.
- `runs/run-004-post-actor-candidate`: exactly the same comparison test, route,
  numerical criteria, dependencies, timing and original factories/player, but
  one isolated additive motor successor installed on the factory-created motor
  instance. Synchronization restored an identity/origin body pose during empty
  assembly; the original foreign-pose guard faulted and departure was refused.
  **No passenger spawn occurred. Candidate rejected; no comparison extension.**

All114 dependency hashes were unchanged after every run. No engine errors or
memory aborts were recorded. Source/tests, logs, full results, memory samples,
exit codes, commands and script hashes are retained. `OBSERVATIONS.json` analyzes
runs1–2; `CONTROLLED_COMPARISON.json` summarizes runs3–4. Earlier failures remain.

The0.10 m screen was chosen before execution, not supplied as engineering/design
acceptance. It is measured from one initial settled location, never reset at
stops. Runs1–2 had0.041077 m initial horizontal settling displacement and a maximum
logged0.137822 m displacement from the original spawn. These are not hidden in
the settled-baseline result. The corrected comparison uses one identical
committed-body spawn/observation definition for both baseline and candidate;
its figures are not substituted for the earlier run's criterion.

## Genuine retained systems used

Current commit: `448eab129169f3c205e7db0662fcf774b869a346`.

- Exact `group4_completion` source models; source024 vehicle factory; boarding
  safety; original cart restraint; single loaded successor motor; operating
  controls. The existing isolated `candidate_only` paths were selected. No
  production `integration_*_admitted` flag was changed.
- Current swimming→float→water-seat→base Player, actual camera, normal capsule,
  gravity and move_and_slide. No surrogate moving body, rider or camera route.
- Original route/pose knots, speeds, acceleration, braking, central/curve limits,
  motor ownership and safety checks. Stops are out-and-back, never wrapped.
- One original18 kg cart and its four loose bottles, unchanged and physical on
  the selected D13 support outside the tram. No freeze, forced attachment, loaded
  experiment or new joint. Original factory cart-handle guard remains installed.
- Five exact compiled support regions: D09_fore_route, D09_aft_route,
  D09_atrium_circulation, D09_salon5_initial_terrace and D13_residential_street_pilot.
  Exact pit proof guard passed before assembly. Other ship surroundings and normal
  streaming were omitted, so this cannot certify whole-ship clearance/playability.
- Actual mounted controls/lamp and original lighting budget. No changed lights,
  streaming bounds, visibility thresholds, memory thresholds or substitute scenery.

The single moving spawn uses cabin-local feet(0,.10,1.40), screened against the
exact source024/026/034 geometry. Live arrival checks preserve the current ray,
normal, floor-height and full standing-capsule tests, excluding Player only, and
add actual-car collider ownership. There are **zero fixture actor position,
velocity, parent or camera writes after that spawn**. Existing Player behavior
remains active with input disabled. The camera heading is world-relative after
initial car-aligned yaw, not forcibly car-relative; no all-direction view claim.

After twelve settling ticks the unchanged0.10 m screen checks floor, car-owned
ray support, original actor_aboard, identities, no held interaction, no joint and
no motion fault. Telemetry is bounded: one-second samples and120 recent frames,
not per-node census. Runs3–4 additionally record committed, target and node poses,
actual player motion and slide-collision shape object. The historic telemetry
key `collider_shape_index` contains the returned CollisionShape3D object, not an
integer. Car-body ownership passed; exact geometry-to-shape labeling is not claimed.

## Diagnosis from source and observations

The original motor writes the Node3D pose immediately with sync_to_physics=false
at priority−30. The current Player uses move_and_slide and the physics platform's
committed velocity. At6 m/s/60 Hz, original node and physical body differ by0.10 m.
Straight samples in both directions also satisfy:

`local_Z + reported_platform_velocity_Z / 60 ≈ 1.4374 m`

The corrected diagnostic arithmetic ranges1.43737745..1.43788190 m,0.505 mm wide.
It was never applied as an actor correction or used to turn a failed run into a
pass. The post-actor baseline directly confirms this phase mismatch. It does not
show missing platform carry, or justify a new player/controller.

Pinned Godot4.6.3 source explains the mechanism:
- Kinematic body_set_state queues new_transform; physics integration derives
  velocity and commits the pose.
- CharacterBody3D reads direct physics-platform state, not an immediately moved
  Node3D's visual transform.
- AnimatableBody synchronization queues a target and reverts the node to its last
  committed transform until the body-state callback.

The rejected31-line successor preserves the existing motor instance and its
state, inherits all original route/safety code, changes only atomic vehicle pose
submission and expected-pose guard timing, and leaves Player untouched. Its
failure exposes a construction prerequisite: the original vehicle factory adds
its body to the tree **before** setting its initial position. Enabling committed
synchronization before an established initial callback can restore its initial
identity pose. The guard correctly refuses travel; no guard was loosened.

If revisited, the smallest coherent follow-on is a named factory/construction
successor that establishes the same initial transform before entering the tree
(or explicitly waits for verified committed initialization), paired with the
atomic motor successor. Preserve the original source/pins and receiving/route
criteria. That change was not authorized for this one comparison and was neither
implemented nor tested. Do not retry this rejected candidate as-is, adopt it, or
force actor/body transforms to mask its failed initialization. Current physical
carry is useful enough to prioritize the independent fixed-clearance repair
rather than prolong motor micro-tests.

Primary source references:
- https://docs.godotengine.org/en/4.6/classes/class_animatablebody3d.html
- https://docs.godotengine.org/en/4.6/classes/class_characterbody3d.html
- https://github.com/godotengine/godot/blob/7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3/scene/3d/physics/animatable_body_3d.cpp
- https://github.com/godotengine/godot/blob/7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3/scene/3d/physics/character_body_3d.cpp
- https://github.com/godotengine/godot/blob/7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3/modules/godot_physics_3d/godot_body_3d.cpp

## Memory, settings and reproducibility

Godot4.6.3 official7d41c59c4, headless, fixed60 Hz simulated physics,
gl_compatibility, no displayed viewport or GPU acceptance. The physics project
setting reports DEFAULT; no backend/engine switch was made. No random procedural
scene generation was added. Wall durations are accelerated test execution times,
not game FPS/latency. No1080p60 claim is possible from these runs.

The independent watchdog requires5 GiB effective available RAM, caps process RSS
at2 GiB, reserves3 GiB system available RAM, samples≤0.25 s and stops on errors or
300 s wall timeout. Test-only writable XDG directories are isolated per run.
All four peak RSS readings are below242 MB; available RAM remained above9.08 GB.
No swap. This does not make a whole-ship launch safe on this cloud host.

`PORTABLE_INPUTS.json` is the complete relative preparation contract for the
exact114 tested inputs:84 SHA-verified PCK entries and30 captured, hash-verified
import-policy files. It pins historical source448 and the full retained e3af0334
PCK SHA256 separately. `prepare_inputs.py` plus the included read-only
`pck_inputs.py` need no recovery_inventory, acquisition ledger, network access or
old absolute paths. Supplied checkout bytes are used only if exact; missing or
newer/different bytes are preserved and replaced only in separate test staging
with the pinned historical fallback. This is not a test of later checkout code.

Both preparation routes were verified without Godot:91 inputs resolved from the
supplied recovered checkout, and an empty-checkout test resolved all114 from the
PCK plus captured import bytes. Every result matched the historical tested hash.
See PORTABLE_PREPARATION_VALIDATION.json. Historical source_map.json and all four
run artifacts remain unchanged; newly generated maps go in a separate directory.

Current script/data overlays are authoritative; the old PCK is a matching byte
and import-cache store, not authority for newer sources. Captured import remap
identity agrees with the exported remap, which omits import parameters. No fresh
editor import/rebuild was performed. Native Blender and complete current editor
closure remain separate recovery work.

Portable preparation (no engine run):

```
python prepare_inputs.py --repo /path/to/checkout --base-pack /path/to/Astraea-e3af0334.pck --out /path/to/separate-prepared-inputs
```

The repo path denotes the root containing Game/. The supplied PCK must be the
exact retained5,088,846,904-byte pack with manifest SHA256; it is not bundled with
this small package. An empty checkout is allowed because exact historical bytes
are available through the pinned pack and captured import policies. Conflicting
files in the output directory are never overwritten; use a new output path.

The retained runtime wrapper remains Linux-specific (/proc memory watchdog and
/usr/local/bin/godot4.6.3). Its input-folder selector is portable; that is not a
claim of tested Windows/macOS runtime portability. No more engine attempts are
authorized simply because commands are present. After parent runtime scheduling:

```
ASTRAEA_CARRY_INPUTS=/path/to/separate-prepared-inputs ASTRAEA_CARRY_RUN=new-original python run_guarded.py
ASTRAEA_CARRY_INPUTS=/path/to/separate-prepared-inputs ASTRAEA_CARRY_RUN=new-baseline ASTRAEA_CARRY_SCRIPT=compare_post_actor_carry.gd ASTRAEA_CARRY_MOTOR=unchanged python run_guarded.py
```

`ASTRAEA_CARRY_EXTEND=1` is the retained extended schedule; it is not an automatic
approval to resume past failure. The rejected sync candidate is retained solely
for review/reproduction of its failure. It is never selected by default.

## Still pending

Full five-stop out-and-back continuity, open-bridge departure-refusal exercise,
ordinary walking/boarding, loaded-cart acceptance, protected fixed-infrastructure
clearance, actual scenic views, full-source editor/build and graphical performance
remain separate. Future scenic refinement must preserve eye-level views of actual
amenities, not enclose the tram or remove its normal ship context.
