# Initial vehicle pose r002 — bounded, unselected

This successor addresses one demonstrated setup defect. The original source factory adds its AnimatableBody3D to the live tree at identity, then assigns CENTRAL position; the retained assembly assigns yaw afterward. In the first fresh baseline, frame0 vehicle velocity was `(-191.1064,3366,-4718.914)` m/s: CENTRAL position `(-3.1851063986930437,56.1,-78.64857410214987)` divided by one 1/60 s tick. At frame4 the cart exceeded the unchanged6 m/s gate with upward velocity67.3329849243164 m/s, four caster contacts against source024 floor0, and no joint. The vehicle velocity had already returned to zero. **The setup defect is established; whether it causes the later caster impulse is not established.**

The separate primitive run stopped before actors/physics: the imported convex contact did not contain the eight exact source corners. It changed zero contacts and is neither a physical pass nor evidence for a floor remedy. Its guard and all first-fixture files remain unchanged. Both actual root-run reports/logs are copied verbatim into `evidence_r001` with hashes; no engine was run by this helper.

Godot4.6.3 source supports the initialization diagnosis: CollisionObject3D supplies its current world transform before assigning its physics space; the first kinematic transform initializes the prior transform, while subsequent changes produce displacement/time-step velocity. AnimatableBody3D also saves its initial transform at tree entry. These facts do not establish the later contact solver's cause. Primary sources: [CollisionObject3D enter-world ordering](https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/scene/3d/physics/collision_object_3d.cpp), [GodotBody3D first transform and kinematic velocity](https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/modules/godot_physics_3d/godot_body_3d.cpp), [AnimatableBody3D initial transform](https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/scene/3d/physics/animatable_body_3d.cpp).

## Narrow implementation

`Game/tram_passenger_successor_20261024/vehicle_initial_pose_r002.gd` assigns the complete initial local Transform3D, name and source metadata before the body's first tree/world admission. The entire original visual/contact-construction suffix is byte-identical, including all imported convex contacts, margins, shape ordering and contact-policy branches. No velocity reset, collision exclusion, live-body repositioning or primitive substitution is made. Generating relative contact transforms at the complete initial yaw can introduce normal floating-point roundoff; bit-identical final contact transforms are not claimed without runtime evidence.

`assembly_initial_pose_r002.gd` differs from the retained assembly only at the fresh factory call: it supplies position and yaw together and removes the after-entry yaw write. Original source builders, body ownership, portals, bridge, station, restraint, motor, control/light bindings and admission-off flags are retained. The original motor still performs its unchanged initialization/normal pose maintenance; this successor does not suppress or reset physics state afterward.

`check_carry_r002.gd` retains the first fixture's source cart/player/four-product creation, original contacts, 120-frame settling, source clamp/joint gates, 15-frame stationary docking, 5 mm/1 mrad dock tolerances and conditional one-metre physical out/return. It accepts only `--floor=baseline`, reports angular as well as linear vehicle velocity, and adds a stationary initialization-velocity gate (below0.001 m/s and0.001 rad/s). No previous threshold is relaxed. There is no extra warmup that hides an initial impulse. One listener-enabled World360 hosts one original actor/cart/product set. Production boarding/motion/joint admission remains off.

## Root-only next check

After checkpointing the exact r001 evidence and r002 source, root can run one bounded unchanged-floor successor:

```sh
godot --headless --fixed-fps 60 --path Game --script res://tram_passenger_successor_20261024/check_carry_r002.gd -- --floor=baseline --report=/tmp/astraea-original-carry-initial-pose-r002.json
```

Compare first vehicle linear/angular velocity and the same caster-settling failure before interpreting later gates. If the initial velocity is cured but caster impulse remains, report the initialization correction separately from the unresolved contact failure; do not promote primitive contacts or call passenger motion proven. If settling passes, the same fixture proceeds only through genuine original joint/dock prerequisites to physical carry. This is not full selected-ship, boarding-route, scenic, visual or performance acceptance.

`SOURCE_PROOF_r002.json`, `CONTRACTS_r002.json` and `PACKAGE_MANIFEST_r002.json` provide exact source/evidence hashes. `seal_r002.py --verify` checks those bytes without an engine. Source-only checks have passed; r002 engine parsing, initial-velocity result, contact outcome and conditional carry remain pending root's sole engine slot. Main selection and all prior revisions are unchanged.
