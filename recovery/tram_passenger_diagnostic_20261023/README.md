Latest: the bounded actual-tram/current-player diagnostic is complete. See [physical-carry/README.md](physical-carry/README.md). Current original carry works through the short leg; extended strict-screen failure and rejected comparison candidate are retained. No production hold cleared. Earlier audit-only JSON files describe their own source-inspection scope.

# Existing tram benchmark: prerequisite and next construction package

Status: source diagnosis complete; no runnable benchmark or runtime acceptance.
Current source: evesloan/Astraea, construction/group1-tidal-d15-20261010,
448eab129169f3c205e7db0662fcf774b869a346. No production files changed.

## Immediate conclusion

Use the existing source024 tram, its single existing loaded-source actuator and the
current original Player. Do not create a substitute vehicle, camera-on-a-path
performance test or replacement player. First prepare a bounded, real physical
passenger-carry diagnostic. Whole-ship moving-tram admission is separately blocked
by a concrete fixed-infrastructure conflict with the protected D09 transit volume.

The selected bootstrap, launcher, presentation and all 21 ship inheritance files
were inspected against current Git blob identities. The selected builder still
calls group4_integrated_receiving.gd, which holds motion, boarding and cart-joint
admission false. No later tram director is referenced by that chain or named in
the complete current scripts tree. This does not rule out a historical version
on another retained branch; none is verified as selected here.

## What actually exists

- One existing Group4OwnedTram_Source024 under ShipSpace/Districts/Group4Completion.
- One Group4LoadedSourceTravelActuator, inherited from the existing source motor.
- The retained 9,964-row pose table passes source-pin, monotonic-range and five
  interpolated station-position checks. It defines an open, bounded guideway,
  not a closed loop. FORWARD and AFT are 935.703093 m apart along the route.
- The five ordered stops are FORWARD, FORE_MIDSHIP, CENTRAL, AFT_MIDSHIP, AFT.
  FORE_MIDSHIP physically docks at Z -241 while retaining catchment Z -216.
- The original controls expose station requests, docking checks, boarding,
  gate/bridge sequencing and secure-departure guards. They do not provide an
  automatic repeated service schedule.
- Current Player is group6_swimming_20261019/player.gd, inheriting the float,
  water-seat and original CharacterBody3D controller. No tram passenger-parenting
  API is present. Its normal move_and_slide platform behavior must be tested,
  not replaced with per-frame position writes.

## Cart hold is not the whole passenger problem

group4_cart_restraint.gd:49-52 already accepts an unladen car when the original
cart is outside it, unlocked, and has no joint. The cart caster/joint fault need
not be solved by disabling cart physics to investigate an unladen passenger ride.
The loaded-cart acceptance field remains false, and all original cart/bottle
identities, forces and stock state remain protected. A passenger-only diagnostic
does not establish loaded-cart travel or permission to open production motion.

## Actual fixed-infrastructure conflict

Current tests/validate_atrium_supports.gd, Git blob
b609552edbd560a0cc8d645f8b11abf0d6755cdb, preserves a radius 2 m, height 4 m cylinder
swept along (0,-72), (0,-56), (40,-52), (40,52), (0,56), (0,72). On D09 the cylinder
occupies Y 52.55 through 56.55. The criterion excludes only Player.

Current-plan-hash-verified source triangles lie inside the CENTRAL start cylinder:

- Moving source024 V2__Tram_Floor triangle 4 centroid:
  (0.369135777, 55.880000001, -72.800000032), horizontal radius 0.881056907 m.
- Fixed source016 V2_Continuous_Web triangle 819 centroid:
  (-0.798605720, 55.549999237, -73.780896505), radius 1.951759067 m.
- Fixed source017 M003_UnderwebGirder_-1.25 triangle 449 centroid:
  (-1.343829513, 55.603332520, -73.439460754), radius 1.969244785 m.

The two fixed meshes have static_trimesh_candidate contact policies. This is a
source-geometric witness, not an executed Godot test. Even excluding the intended
moving tram would leave fixed infrastructure in the protected volume. Do not
weaken the criterion or exempt the fixed meshes to manufacture a pass.

The already adopted four pit cuts are a different matter: they remove exactly
24.8 m² across D09_fore_route, D09_aft_route and D09_atrium_circulation and are
explicitly outside the protected axis. Keep the exact pit successor guard and
all other floor owners intact. Moving or widening those cuts is not a justified
repair for the conflict above.

## Next package, in order

1. Finish only the real tram/player diagnostic dependency closure. The 21 pinned
   tram GLBs, totaling 5,095,876 bytes, have now been recovered and verified from
   retained bytes. KNOWN_FIXTURE_GAPS.json records the initial remaining literal
   dependencies, not a complete closure. Resolve their own imports, textures,
   contracts and source pins before any Godot import or execution.
2. Add one new bounded diagnostic, following NEXT_PACKAGE.md. It can test real
   CharacterBody platform carry headlessly without constructing the full ship.
   It must use retained factories/controllers, not CarryProbe or a synthetic tram.
   This is source physics evidence only, with production flags untouched.
3. Recover the native/generator/interface ownership of source016 and source017.
   Reconcile their exact fixed contact geometry with the unchanged protected
   reservation, master chapter 32 and route contract. Author a named immutable
   successor only after a concrete, supported physical repair is determined.
   No raised track, alternative route, exclusion or revised acceptance is chosen
   by this package. If preservation cannot be achieved without changing a
   protected interface, surface that exact design conflict rather than guess.
4. Once the fixed conflict and genuine carry are resolved, run the unchanged
   receiving/route criteria against the selected current main. Only then design
   narrow unladen-passenger admission. Loaded-cart admission remains separate.
5. Finally add the opt-in out-and-back benchmark described in NEXT_PACKAGE.md.
   Keep the default bootstrap and ordinary launch behavior unchanged.

## Completed and pending evidence

Completed: current source identities; current selected startup chain; original
player/motor/safety ownership; current model recovery pins; exact pose-table and
station checks; governing master chapters 5, 14 and 32; source triangle witnesses.

Pending: diagnostic dependency closure; GDScript/import/physics checks; actual
unladen moving-player support; fixed receiving repair; current-main route collision
and boarding checks; graphical startup; repeated-lap resource recovery; target
hardware FPS and matching playable build. No benchmark numbers were generated.

The original source-travel test is an isolated older fixture, asserts inactive
flags inconsistent with today's active source plans, and samples contacts only
every 180 physics frames. The received-player test covers lifts/platform walking,
not moving tram carry. Preserve these tests as history; do not relax assertions
and call them current whole-ship acceptance.

## Runtime and handoff limits

Pinned engine: Godot 4.6.3.stable.official.7d41c59c4, gl_compatibility. The current
launcher defaults to 640×360 world rendering even though the window is 1280×720.
Target measurement requires the actual world and post viewports at 1920×1080,
not merely a larger window. The stated target is 60 FPS / 16.67 ms on the owner
target hardware, not fixed-step headless execution.

Whole-ship launch on this cloud host is unsafe to assume: approximately 9.97 GB
total RAM, approximately 8.9 GB available, no swap, versus a previously observed
approximately 12.9 GiB private-memory full walking run reported by the parent.
Require fresh preflight and a conservative external process/system-memory abort
before any future launch. Do not change production streaming distances, visibility,
lighting, memory thresholds or source detail to make the test fit.

Run audit_current_sources.py only for read-only source evidence. It does not invoke
Godot. JSON outputs contain pins and facts, not test acceptance. Root owns review,
publication and the independently verified checkpoint; this directory has not
been published by its author.
