# Astraea tram: retained section-contract conflict

Status: construction held at a genuine protected-interface decision. This is a
bounded source review, not a clearance repair or runtime acceptance. No candidate
geometry, native revision, controller change, production adoption or publication
was made. Root remains the sole publisher.

Reviewed source checkpoint: `de6803e7f2054cd20c2e1580a1f5c47e3f792db0`.

## Finding that changes the next package

The obstruction is not limited to a removable web or an isolated receiving girder.
Both continuous rail heads, the continuous web and both underweb girders occupy
the current protected D09 volume. The exact route, rail height and wheel gauge
cannot all stay fixed while these rails become clear of that volume. Removing,
masking or merely thinning the web/girders therefore cannot close this gate.

There is also a retained contract mismatch: the native-source validators preserve
a four-metre-WIDE lower corridor with only 3.05 m of vertical clearance, whereas
the current actual-main test requires four metres of width AND height over the
same central polyline at the D09 deck datum. The master identifies the polyline
as the service-tram swept path but does not set its vertical datum in that clause.
This review cannot choose which interpretation should govern a revised design.

Under the unchanged current test, the source geometry is demonstrably obstructing.
That is a real failed geometric condition, not a hypothetical concern. It does
not by itself prove whether the intended architectural correction is a relocated
tram, a distinct lower circulation corridor, or a formally reconciled running
reservation. Calling the test obsolete or declaring the source's narrower check
equivalent would invent a decision the evidence does not supply.

## What the retained contracts actually say

### Master intent

`Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json`, chapter 32,
body 564 (lines 5495-5501), says to protect the starboard service-tram swept path
through `(0,-72),(0,-56),(40,-52),(40,52),(0,56),(0,72)`, including the loaded cart
and boarding approaches. It also says a track centreline is insufficient evidence.
That paragraph specifies X/Z but no Y, four-metre height or below-track pedestrian
interpretation.

Chapter 5, body 145 (lines 1307-1313), says rails, piers, trim, door leaves, stock
cabinets and decorative planters all count as physical obstructions. Body 147 says
a structural revision invalidates affected old route results. Chapter 32,
body 571 (lines 5544-5550), requires a decision when a genuine conflict changes a
protected interface, capacity or engineering constraint. Chapter 32 is refinement
of the existing ship, not permission for wholesale replacement.

Chapter 5, body 138 distinguishes the player's physical service tram from screened,
finite-time abstract guest transport. The user's passenger-view ambition does not
by itself admit additional guest-service capacity or clear the existing motion hold.

The master and its current application require useful internal views, real
architectural transitions and normal first-person review. Their view direction
does not authorize new holes through occupied rooms, deleting adjacent amenities,
fake occluders or sacrificing support to make the clearance check pass.

### Current executable reservation

`Game/tests/validate_atrium_supports.gd:34-46`, current Git blob
`b609552edbd560a0cc8d645f8b11abf0d6755cdb`, creates a radius-2 m, height-4 m
cylinder over that six-point route. For D09 it centres the cylinder at
`deck_y[8]+2.05`: Y 52.55 through 56.55. Only the actual Player is excluded.
Both the initial overlap and full segment cast must be unobstructed.

The test calls this four-metre-wide, four-metre-high reserved transit clearance,
not explicitly a passenger-only corridor below the track. Its source fixes the
volume even though its precise architectural interpretation is not settled here.
Its final statement separately disclaims structural engineering, loaded-cart and
tram-dynamics acceptance. The current integration owner still records the
protected four-metre D09 receiving hold and keeps motion, boarding and cart joint
admission false (`Game/scripts/group4_integrated_receiving.gd:18-26`).

### Native-source interpretation, demonstrably narrower

Paths in this paragraph are under
`BlenderCatalogue/assets/group4_tram_connections_20261009/`.

- `port_successor_002/validate_successor.py:36-41` labels its check the lower4m
  corridor but allows parts above Y 55.55. It checks X -2..2 against
  Y 52.5..55.55, not a four-metre-high swept cylinder along the central bypass.
- `receiving_module_003/validate_receiving.py:69` repeats those X/Y bounds. Its
  reported zero lower-axis intrusions is not evidence that the current 4x4 test
  passes, and it is not an equivalent polyline sweep.
- `port_successor_002/build_successor.py:190-191` authors the web at
  Y 55.55..55.68 and the two rails at Y 55.68..55.74. Its
  `SUCCESSOR_INTERFACE.json` binds rail head Y 55.74, car/boarding floor Y 56.1,
  soffit Y 55.55 and unchanged route vertices. The exact interface SHA-256 agrees
  with the current selected travel manifest.
- `receiving_module_003/build_receiving.py:49-61` explicitly preserves a 3.05 m
  soffit and places the two receiving girders at Y 55.55..55.71. Its README
  likewise says 3.05 m lower-axis clearance.
- `receiving_module_003/build_receiving.py:24-28` and `plan_receiving.py:45`
  separately preserve a running-clearance top at Y 60.1, put headers above it at
  Y 60.18..60.50 and use actual D10 underside Y 60.76. Together with boarding
  floor Y 56.1 this is arithmetically a four-metre upper running band, but that
  arithmetic must not be promoted to a master-approved replacement test.

Thus the sources explicitly distinguish a lower corridor from a higher running
clearance. They do NOT explicitly establish that the master intended the existing
deck-based cylinder to be replaced by that upper band. Nor do they establish an
approved four-metre-high circulation space below this guideway.

## Direct geometry and integration evidence

`GEOMETRY_WITNESSES.json` contains one entire nondegenerate triangle strictly
inside the unchanged CENTRAL-start cylinder for each of these five fixed meshes:

- source016 `V2_Continuous_Web`, triangle 851, Y approximately 55.55..55.68.
- source016 `V2_Continuous_Rail_-0.86`, triangle 826, Y approximately 55.68..55.74.
- source016 `V2_Continuous_Rail_0.86`, triangle 834, Y approximately 55.68..55.74.
- source017 `M003_UnderwebGirder_-1.25`, triangle 456, Y approximately 55.55..55.71.
- source017 `M003_UnderwebGirder_1.25`, triangle 459, Y approximately 55.55..55.71.

The JSON retains full vertices, source hashes and exact floating-point bounds.
All vertices of each witness are strictly inside the convex cylinder, so this is
positive intersection evidence, not an AABB-only inference or an absence claim.
These are five examples, not an exhaustive inventory of obstructing receivers.

The local runtime GLBs agree with both the current selected manifest's SHA-256
and their original source-family Git blob SHA-1 at the reviewed checkpoint.
Each selected mesh has `static_trimesh_candidate` policy. The current
`group4_completion.gd:40-58` collects every non-detail member into the static
contact cache, without an offset on these root meshes. Their geometry is not
intended visual-only decoration. No Godot test was executed in this review.

Removing the moving car from the reservation does not affect any of these five
fixed witnesses. No player, cart, bottle, motor, rail gauge, collision mask,
query margin, test assertion or production admission field was changed.

## Smallest safe next construction package

First reconcile the section contract, before selecting a new member or load path.
The necessary design decision is precise: what vertical band belongs to the
protected central service-tram reservation, and what independent lower circulation
width/headroom must remain beneath or beside it? Preserve the master polyline,
existing deck datums, amenity sightlines, programme ownership and accepted north
physical dock/catchment distinction unless a separately documented decision
explicitly changes the affected interface.

Two coherent future branches can then be scoped, neither selected here:

1. If the current D09-based 4x4 clear volume remains absolute, a support-only edit
   at the retained rail datum is impossible. A coordinated track/boarding section
   or horizontal-alignment proposal is required, covering source016, source017,
   affected stations, lift/bridge interfaces, exact receiving owners and the
   source-derived pose data together. That proposal must identify any protected
   interface changes before implementation; it must retain current controller
   ownership, actual car/cart/stock identities and meaningful amenity views.
   A simple raise is not an accepted solution: lifting the present soffit just
   above 56.55 would put boarding above 57.1; carrying the present four-metre
   upper-band interpretation with it puts its top above 61.1, already above the
   recorded D10 underside 60.76. Those numbers explain why a full section,
   not a guessed one-metre offset, is needed. They are not a chosen design.

2. If an explicit protected-interface decision confirms distinct lower
   circulation and upper rollingstock bands, first record both complete volumes,
   their users and their receiving boundaries. Only then define the smallest
   physical native successor, if any, required by those approved bands. Track
   and support contacts must remain physical; replacing a collision mask or
   exempting the rails is not construction. Any revised acceptance must add
   truthful checks of both bands and the loaded car/boarding envelope, preserve
   the old test as historical evidence and obtain the decision required for a
   changed protected interface. This review does not authorize that revision.

Neither branch starts by deleting members, making rail collisions disappear,
moving/widening the four approved pits, rewriting the actor or motor, or claiming
the existing source-only PASS resolves the present integration hold.

After that decision, the first actual successor should be small and immutable:
native and recipe alongside its export, explicit receiving-member ownership,
before/after pins, unchanged unrelated source and targeted checks against the
approved section. Production adoption waits for the unchanged-or-explicitly-
reconciled actual-main criteria and normal-height passenger views. Whole-ship
closure, full graphical acceptance and hardware performance remain separate.

## What was and was not done

Done: read complete relevant master chapters, current overlays, exact current
integration owner, source recipes/interfaces and existing clearance evidence;
recover and verify 11 retained text inputs (199,150 bytes); verify current content
pins and two GLBs; produce five fixed positive intersection witnesses; verify
all inspected production input bytes unchanged before/after the static audit.

The two native Blender files are verified as retained in the current remote
directory, with identity/size in `INPUT_RECEIPT.json`. Their binary bytes were not
downloaded or opened because the recipe/runtime evidence already establishes the
protected-interface decision. This package is not a complete native rebuild kit.

Not done: a native geometry correction, a new physical load path, a Godot or
Blender launch, an engine import, a motion experiment, a display attempt, a
whole-ship build, production edits, file removal, asset downloads in bulk or
publication. No full-suite, finished-art, playable-build or 60 FPS claim.

The construction action was stopped by the evidenced design conflict, not by an
access denial. Future geometry implementation is pending a section-contract
decision; no uncertain mutation or upload needs retrying.
